"""
llm_processor.py - LLM 智能处理模块

功能：将 docx_parser 输出的原始段落发送给 LLM，进行结构化处理
- 确认/修正标题
- 生成摘要（≤120字）
- 判断文章类型（news 学院活动新闻稿 / interview 采访 / lecture 讲座）
- 识别小节标题 vs 正文段落
- 提取署名信息
- 识别需要强调的关键词

调用方式：通过 subprocess 调用 claude CLI 的 --print 模式
"""

import json
import os
import subprocess
import sys


# LLM 的 system prompt
SYSTEM_PROMPT = """你是一个专业的公众号推文编辑助手。你的任务是分析学院新闻稿的原始段落数据，输出结构化的 JSON。

你必须严格按照以下 JSON 格式输出，不要输出任何其他内容（不要 markdown 代码块，不要解释）：

{
  "title": "文章标题",
  "summary": "一句话摘要，≤120字，包含时间、地点、人物、事件",
  "category": "news(学院活动新闻稿) 或 interview(采访) 或 lecture(讲座)",
  "credits": {
    "文字": ["张正烽", "周芷轩"],
    "图片": ["李明"],
    "美编": ["王芳"],
    "责编": ["赵刚"],
    "审核": ["刘教授"]
  },
  "sections": [
    {"type": "heading", "content": "小节标题内容"},
    {"type": "paragraph", "content": "正文段落内容", "emphasis_keywords": ["关键词1", "关键词2"]},
    {"type": "image", "filename": "img_001.jpg"},
    ...
  ]
}

判断规则：
1. 第一个文字段落通常是标题，确认后放入 title 字段，不要重复放入 sections
2. 末尾的短段落如果包含署名关键词，是署名信息，解析后放入 credits 字段（dict格式），不要放入 sections。署名可能占1~3个段落，关键词包括：文字/文编→统一归为"文字"，图片/摄影→统一归为"图片"，美编、责编、审核。格式示例："文字 张正烽 周芷轩" 或 "文编｜张正烽" 等
3. 短文字段落（≤20字）且含有书名号或冒号或明显是标题格式的，标记为 heading
4. 其余文字段落标记为 paragraph，提取2-4个关键词
5. 图片段落保持原样，type 为 image
6. emphasis_keywords 选择段落中最重要的名词、专有名词或关键概念"""


def _build_user_prompt(raw_paragraphs):
    """构建发送给 LLM 的用户 prompt"""
    lines = ["以下是从 Word 文档中提取的原始段落数据，请分析并结构化：\n"]
    for i, para in enumerate(raw_paragraphs):
        if para["type"] == "text":
            lines.append(f"[段落{i}] 类型:文字 样式:{para.get('style', 'Normal')}")
            lines.append(f"  内容: {para['content']}")
        elif para["type"] == "image":
            lines.append(f"[段落{i}] 类型:图片 文件:{para['filename']}")
        elif para["type"] == "text_with_image":
            lines.append(f"[段落{i}] 类型:文字+图片 样式:{para.get('style', 'Normal')}")
            lines.append(f"  内容: {para['content']}")
            lines.append(f"  图片: {', '.join(para['images'])}")
        lines.append("")
    return "\n".join(lines)


def process_with_llm(raw_paragraphs, provider="claude"):
    """调用 LLM 处理原始段落数据

    Args:
        raw_paragraphs: docx_parser 输出的 raw_paragraphs 列表
        provider: LLM 提供者，"claude" 或 "gemini"

    Returns:
        结构化的 JSON dict，包含 title, summary, category, author, sections
    """
    user_prompt = _build_user_prompt(raw_paragraphs)
    full_prompt = f"{SYSTEM_PROMPT}\n\n---\n\n{user_prompt}"

    # 通过 stdin 传入 prompt，避免命令行参数过长被截断
    if provider == "claude":
        cmd = ["claude", "-p", "--model", "sonnet",
               "--append-system-prompt", "只输出纯JSON，不要markdown代码块"]
    elif provider == "gemini":
        cmd = ["gemini", "-p"]
    else:
        raise ValueError(f"不支持的 LLM 提供者: {provider}")

    print(f"[LLM] 正在调用 {provider} 处理文本...", file=sys.stderr)

    try:
        # 清理环境变量，避免嵌套 Claude Code 会话检测
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)

        result = subprocess.run(
            cmd,
            input=full_prompt,  # 通过 stdin 传入完整 prompt
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            shell=True,  # Windows 下需要 shell=True 来查找 .cmd 脚本
            env=env,
        )

        if result.returncode != 0:
            print(f"[LLM] 调用失败，返回码: {result.returncode}", file=sys.stderr)
            print(f"[LLM] stderr: {result.stderr}", file=sys.stderr)
            return _fallback_process(raw_paragraphs)

        output = result.stdout.strip()

        # 尝试从输出中提取 JSON（LLM 可能会包裹在 markdown 代码块中）
        json_str = _extract_json(output)
        parsed = json.loads(json_str)

        print(f"[LLM] 处理完成", file=sys.stderr)
        return parsed

    except subprocess.TimeoutExpired:
        print("[LLM] 调用超时（120s），使用回退处理", file=sys.stderr)
        return _fallback_process(raw_paragraphs)
    except json.JSONDecodeError as e:
        print(f"[LLM] JSON 解析失败: {e}", file=sys.stderr)
        print(f"[LLM] 原始输出:\n{output}", file=sys.stderr)
        return _fallback_process(raw_paragraphs)
    except FileNotFoundError:
        print(f"[LLM] 找不到 {provider} CLI，使用回退处理", file=sys.stderr)
        return _fallback_process(raw_paragraphs)


def _extract_json(text):
    """从 LLM 输出中提取 JSON 字符串

    处理可能的 markdown 代码块包裹
    """
    # 尝试直接解析
    text = text.strip()
    if text.startswith("{"):
        return text

    # 尝试从 ```json ... ``` 中提取
    import re
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 尝试找到第一个 { 和最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return text[start:end + 1]

    raise json.JSONDecodeError("无法从 LLM 输出中提取 JSON", text, 0)


def _fallback_process(raw_paragraphs):
    """LLM 不可用时的回退处理：基于简单规则进行结构化

    规则：
    - 第一个文字段落 → 标题
    - 末尾短段落含署名关键词 → 解析为 credits dict
    - 根据标题/正文关键词推断分类
    - 其余保持原样
    """
    import re
    print("[LLM] 使用回退规则处理...", file=sys.stderr)

    title = ""
    credits = {}
    sections = []

    # 找到所有文字段落的索引
    text_indices = [
        i for i, p in enumerate(raw_paragraphs) if p["type"] in ("text", "text_with_image")
    ]

    if not text_indices:
        return {
            "title": "未知标题",
            "summary": "",
            "category": "news",
            "credits": {},
            "sections": [],
        }

    # 标题识别：段落[0]如果较短（≤50字），大概率是标题；否则是导语，标题留空（由调用方用文件名补充）
    first_text_idx = text_indices[0]
    first_text = raw_paragraphs[first_text_idx]["content"]
    if len(first_text) <= 50:
        title = first_text
        skip_first = True  # 标记段落[0]已作为标题，不放入 sections
    else:
        title = ""  # 留空，由 main.py 用文件名补充
        skip_first = False  # 段落[0]是导语，仍放入 sections

    # --- 署名识别 ---
    # 署名关键词：原始形式 → 统一名称
    CREDIT_ALIASES = {
        "文字": "文字", "文编": "文字",
        "图片": "图片", "摄影": "图片",
        "美编": "美编",
        "责编": "责编",
        "审核": "审核",
    }
    ALL_CREDIT_KEYWORDS = list(CREDIT_ALIASES.keys())

    # 从末尾向前扫描，最多检查3个文字段落作为署名区域
    credit_indices = set()  # 被识别为署名的段落索引
    for idx in reversed(text_indices[-3:]):
        para_text = raw_paragraphs[idx]["content"]
        # 署名段落特征：较短（≤80字）且包含署名关键词
        if len(para_text) <= 80 and any(kw in para_text for kw in ALL_CREDIT_KEYWORDS):
            credit_indices.add(idx)
            # 解析这一段中的署名
            _parse_credit_line(para_text, credits, CREDIT_ALIASES)
        else:
            break  # 遇到非署名段落就停止向前扫描

    # --- 分类推断 ---
    category = _infer_category(title, raw_paragraphs)

    # --- 构建 sections ---
    for i, para in enumerate(raw_paragraphs):
        # 跳过已作为标题的段落
        if skip_first and i == first_text_idx:
            continue
        # 跳过署名段落
        if i in credit_indices:
            continue

        if para["type"] == "image":
            sections.append({"type": "image", "filename": para["filename"]})
        elif para["type"] == "text":
            content = para["content"]
            # 判断是否为小节标题：短文字 + 含有特定模式
            is_heading = (
                len(content) <= 25
                and (
                    "：" in content or ":" in content  # 冒号格式：第一篇章：XXX
                    or "篇章" in content               # 篇章关键词
                    or re.match(r"^[-—]+.+[-—]+$", content)  # 破折号包裹：-开幕式-
                    # 极短纯文字（≤6字）且无标点 → 大概率是小节标题（如"结语""前言"）
                    or (len(content) <= 6 and not re.search(r"[，。、；！？,.;!?]", content))
                )
            )
            if is_heading:
                sections.append({"type": "heading", "content": content})
            else:
                sections.append({
                    "type": "paragraph",
                    "content": content,
                    "emphasis_keywords": [],
                })
        elif para["type"] == "text_with_image":
            sections.append({
                "type": "paragraph",
                "content": para["content"],
                "emphasis_keywords": [],
            })
            for img in para.get("images", []):
                sections.append({"type": "image", "filename": img})

    return {
        "title": title,
        "summary": "",
        "category": category,
        "credits": credits,
        "sections": sections,
    }


def _parse_credit_line(text, credits, aliases):
    """解析一行署名文本，将结果合并到 credits dict 中

    支持多种分隔格式：
    - "文字 张正烽 周芷轩"
    - "文编｜张正烽"
    - "文字：张正烽、周芷轩"
    - "文字/图片 张正烽" （一人多职）
    """
    import re
    # 按常见分隔符拆分为多段
    # 先按换行拆分
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # 尝试匹配 "关键词 + 分隔符 + 人名列表" 的模式
        for keyword in sorted(aliases.keys(), key=len, reverse=True):
            if keyword not in line:
                continue
            # 找到关键词后，提取其后面的人名
            pattern = re.escape(keyword) + r"[：:｜|\s]+"
            match = re.search(pattern, line)
            if match:
                rest = line[match.end():].strip()
                # 在人名列表遇到下一个署名关键词时截断
                next_kw_pos = len(rest)
                for other_kw in aliases.keys():
                    pos = rest.find(other_kw)
                    if pos > 0:
                        next_kw_pos = min(next_kw_pos, pos)
                rest = rest[:next_kw_pos].strip()
                # 按空格、顿号、逗号分隔人名
                names = re.split(r"[、，,\s]+", rest)
                names = [n.strip() for n in names if n.strip()]
                unified = aliases[keyword]
                if names:
                    credits.setdefault(unified, []).extend(names)


def _infer_category(title, raw_paragraphs):
    """根据标题和正文关键词推断文章分类

    分类（依据美编规范）：
    - news: 学院活动新闻稿（默认）
    - interview: 采访
    - lecture: 讲座
    """
    # 拼接标题和前几段正文用于关键词匹配
    all_text = title
    text_count = 0
    for p in raw_paragraphs:
        if p["type"] in ("text", "text_with_image") and text_count < 5:
            all_text += " " + p.get("content", "")
            text_count += 1

    # 讲座关键词
    if any(kw in all_text for kw in ["讲座", "报告会", "学术报告", "主讲人", "主讲嘉宾"]):
        return "lecture"

    # 采访关键词
    if any(kw in all_text for kw in ["采访", "专访", "对话", "访谈", "Q&A", "问答"]):
        return "interview"

    # 默认归为新闻稿
    return "news"


if __name__ == "__main__":
    # 测试用：从 stdin 读取 docx_parser 的输出
    import sys
    data = json.load(sys.stdin)
    result = process_with_llm(data["raw_paragraphs"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
