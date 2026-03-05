"""
tool2_layout/renderer.py - 渲染引擎

读取 extracted.json，根据 category 选择模板，渲染为微信公众号兼容的 HTML。
"""

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from tool2_layout import components


# 模板目录
TEMPLATES_DIR = Path(__file__).parent / "templates"

# 强调关键词的颜色
EMPHASIS_COLOR_BLUE = "rgb(32, 90, 171)"
EMPHASIS_COLOR_RED = "rgb(185, 27, 21)"

# 模板 → 强调色 映射
TEMPLATE_EMPHASIS_COLOR = {
    "news": EMPHASIS_COLOR_BLUE,
    "news_blue2": EMPHASIS_COLOR_BLUE,
    "news_red": EMPHASIS_COLOR_RED,
    "news_cyan": EMPHASIS_COLOR_BLUE,
    "news_red2": EMPHASIS_COLOR_RED,
    "news_red3": EMPHASIS_COLOR_RED,
    "news_purple": EMPHASIS_COLOR_BLUE,
    "lecture": EMPHASIS_COLOR_BLUE,
}

# 讲座模板默认署名占位（当 credits 为空时使用）
LECTURE_DEFAULT_CREDIT = "周芷轩"


def _build_paragraph_html(text, emphasis_keywords=None, emphasis_color=None):
    """将纯文本段落转为 HTML，对关键词施加彩色加粗

    Args:
        text: 段落纯文本
        emphasis_keywords: 需要强调的关键词列表
        emphasis_color: 强调颜色（默认蓝色）

    Returns:
        格式化后的 HTML 字符串（含 <p> 标签）
    """
    color = emphasis_color or EMPHASIS_COLOR_BLUE

    # 先做基本 HTML 转义（仅对 & < > 进行转义，保留中文）
    html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # 应用关键词强调
    if emphasis_keywords:
        for kw in emphasis_keywords:
            kw_escaped = kw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if kw_escaped in html:
                styled = (
                    f'<span style="color: {color}; box-sizing: border-box;">'
                    f'<strong style="box-sizing: border-box;">{kw_escaped}</strong></span>'
                )
                html = html.replace(kw_escaped, styled)

    return (
        f'<p style="white-space: normal; margin: 0px; padding: 0px; box-sizing: border-box;">'
        f'{html}</p>'
    )


def _resolve_image_path(filename, images_dir):
    """解析图片路径，本地预览用 file:/// 绝对路径

    Args:
        filename: 图片文件名（如 img_001.jpg）
        images_dir: 图片目录路径字符串

    Returns:
        可在浏览器中打开的图片 URL
    """
    if not images_dir or not filename:
        return ""
    img_path = Path(images_dir) / filename
    if img_path.exists():
        # 本地预览：使用 file:/// 协议 + 绝对路径
        abs_path = img_path.resolve()
        # Windows 路径转 URL 格式
        return abs_path.as_uri()
    # 如果文件不存在，返回原始相对路径（可能是 CDN URL）
    return filename


def _prepare_news_sections(sections, images_dir, emphasis_color=None):
    """预处理新闻稿的 sections，生成渲染所需的数据

    Returns:
        处理后的 section 列表，每个 section 包含 type 和渲染需要的字段
    """
    prepared = []
    heading_counter = 0
    for sec in sections:
        if sec["type"] == "paragraph":
            content_html = _build_paragraph_html(
                sec["content"],
                sec.get("emphasis_keywords"),
                emphasis_color=emphasis_color,
            )
            prepared.append({
                "type": "paragraph",
                "content_html": content_html,
            })
        elif sec["type"] == "image":
            src = _resolve_image_path(sec.get("filename", ""), images_dir)
            prepared.append({
                "type": "image",
                "src": src,
                "in_group": False,  # 后续标记是否属于连续图片组
            })
        elif sec["type"] == "caption":
            prepared.append({
                "type": "caption",
                "content": sec["content"],
            })
        elif sec["type"] == "heading":
            heading_counter += 1
            prepared.append({
                "type": "heading",
                "content": sec["content"],
                "number": heading_counter,
            })

    # 标记连续图片组（3张及以上连续图片才标记为 in_group）
    _mark_image_groups(prepared)

    return prepared


def _mark_image_groups(prepared):
    """标记连续3张及以上的图片为 in_group=True，用于红色模板图片样式轮换"""
    i = 0
    while i < len(prepared):
        if prepared[i].get("type") == "image":
            # 找到连续图片的结束位置
            j = i
            while j < len(prepared) and prepared[j].get("type") == "image":
                j += 1
            run_length = j - i
            if run_length >= 3:
                for k in range(i, j):
                    prepared[k]["in_group"] = True
            i = j
        else:
            i += 1


def _prepare_lectures(sections, images_dir):
    """从 sections 中提取讲座数据

    讲座类型的 extracted.json 可能有两种格式：
    1. sections 中直接包含 type=lecture 的块（LLM 处理后）
    2. 顶层有 lectures 列表（直接传入）

    Returns:
        讲座列表，每个元素包含 title, speaker, host, time, location, poster, photo, abstract, bio
    """
    lectures = []
    current = None

    for sec in sections:
        sec_type = sec.get("type", "")

        if sec_type == "lecture":
            # LLM 可能直接输出了 lecture 类型的块
            lectures.append({
                "title": sec.get("title", ""),
                "speaker": sec.get("speaker", ""),
                "host": sec.get("host", ""),
                "time": sec.get("time", ""),
                "location": sec.get("location", ""),
                "poster": _resolve_image_path(sec.get("poster", ""), images_dir),
                "photo": _resolve_image_path(sec.get("photo", ""), images_dir),
                "abstract": sec.get("abstract", ""),
                "bio": sec.get("bio", ""),
            })
        elif sec_type == "image":
            # 讲座海报通常是第一张图片
            if current is None:
                current = _empty_lecture()
            if not current["poster"]:
                current["poster"] = _resolve_image_path(sec.get("filename", ""), images_dir)
            elif not current["photo"]:
                current["photo"] = _resolve_image_path(sec.get("filename", ""), images_dir)
        elif sec_type == "paragraph":
            if current is None:
                current = _empty_lecture()
            # 尝试从正文中提取讲座信息
            content = sec.get("content", "")
            _try_parse_lecture_info(content, current)
        elif sec_type == "heading":
            # 新讲座的标题
            if current and (current["title"] or current["abstract"]):
                lectures.append(current)
            current = _empty_lecture()
            current["title"] = sec.get("content", "")

    # 最后一个讲座
    if current and (current["title"] or current["abstract"]):
        lectures.append(current)

    return lectures


def _empty_lecture():
    """返回空的讲座数据结构"""
    return {
        "title": "",
        "speaker": "",
        "host": "",
        "time": "",
        "location": "",
        "poster": "",
        "photo": "",
        "abstract": "",
        "bio": "",
    }


def _try_parse_lecture_info(text, lecture):
    """尝试从文本中解析讲座信息字段"""
    # 尝试匹配 "报告人：XXX" 这样的模式
    patterns = {
        "speaker": r"报告人[：:]\s*(.+)",
        "host": r"主持人[：:]\s*(.+)",
        "time": r"时间[：:]\s*(.+)",
        "location": r"(?:地点|地址)[：:]\s*(.+)",
    }
    matched = False
    for field, pattern in patterns.items():
        m = re.search(pattern, text)
        if m and not lecture[field]:
            lecture[field] = m.group(1).strip()
            matched = True

    # 如果没匹配到字段标签，尝试判断是摘要还是简介
    if not matched:
        if not lecture["abstract"]:
            lecture["abstract"] = text
        elif not lecture["bio"]:
            lecture["bio"] = text


def render(extracted_json_path, head_img=None, tail_img=None, template_name=None):
    """读取 extracted.json，根据 category 选模板，渲染为 HTML

    Args:
        extracted_json_path: extracted.json 文件路径
        head_img: 头图路径（可选，覆盖默认 GIF）
        tail_img: 尾图路径（可选，覆盖默认 GIF）
        template_name: 指定模板名称（可选，覆盖自动选择）
                       可选值: news, news_blue2, lecture

    Returns:
        渲染后的 HTML 字符串
    """
    json_path = Path(extracted_json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    category = data.get("category", "news")
    sections = data.get("sections", [])
    credits = data.get("credits", {})
    images_dir = data.get("images_dir", "")
    title = data.get("title", "")

    # 解析 images_dir 为绝对路径
    if images_dir and not Path(images_dir).is_absolute():
        # 优先尝试从工作目录解析（tool1 输出的路径通常基于 cwd）
        candidate_cwd = Path(images_dir).resolve()
        # 也尝试基于 json 所在目录解析（images_dir 可能是 "images" 这样的相对路径）
        candidate_json = (json_path.parent / Path(images_dir).name).resolve()
        if candidate_cwd.is_dir():
            images_dir = str(candidate_cwd)
        elif candidate_json.is_dir():
            images_dir = str(candidate_json)
        else:
            # 兜底：直接用 json 所在目录下的 images 子目录
            images_dir = str((json_path.parent / "images").resolve())

    # 处理头尾图
    head_img_html = ""
    tail_img_html = ""

    if head_img:
        head_img_path = Path(head_img)
        if head_img_path.exists():
            head_img_html = components.head_image(head_img_path.resolve().as_uri())
        else:
            head_img_html = components.head_image(head_img)
    else:
        # 使用默认 GIF
        head_img_html = components.head_image()

    if tail_img:
        tail_img_path = Path(tail_img)
        if tail_img_path.exists():
            tail_img_html = components.tail_image(tail_img_path.resolve().as_uri())
        else:
            tail_img_html = components.tail_image(tail_img)
    else:
        tail_img_html = components.tail_image()

    # 设置 Jinja2 环境
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,  # 不转义，我们手动控制 HTML
    )

    # 注册组件函数到模板
    env.globals.update({
        # 新闻稿（蓝色模板1）
        "text_card": components.text_card,
        "image_frame": components.image_frame,
        "heading_block": components.heading_block,
        "news_separator": components.news_separator,
        "credits_block": components.credits_block,
        # 讲座
        "decorator_line": components.decorator_line,
        "lecture_poster": components.lecture_poster,
        "lecture_info": components.lecture_info,
        "lecture_card": components.lecture_card,
        "decorator_gif": components.decorator_gif,
        # 蓝色模板2
        "blue2_frame_open": components.blue2_frame_open,
        "blue2_frame_close": components.blue2_frame_close,
        "blue2_image": components.blue2_image,
        "blue2_paragraph": components.blue2_paragraph,
        # 红色模板（党建）
        "red_separator": components.red_separator,
        "red_dashed_line": components.red_dashed_line,
        "red_text_card": components.red_text_card,
        "red_activity_banner": components.red_activity_banner,
        "red_numbered_heading": components.red_numbered_heading,
        "red_text_block": components.red_text_block,
        "red_image": components.red_image,
        "red_image_with_ribbon": components.red_image_with_ribbon,
        "red_image_with_bar": components.red_image_with_bar,
        "red_credits": components.red_credits,
        # 青色模板
        "cyan_text_card": components.cyan_text_card,
        "cyan_numbered_heading": components.cyan_numbered_heading,
        "cyan_text_block": components.cyan_text_block,
        "cyan_image": components.cyan_image,
        "cyan_credits": components.cyan_credits,
        # 红色模板2
        "red2_frame_open": components.red2_frame_open,
        "red2_frame_close": components.red2_frame_close,
        "red2_paragraph": components.red2_paragraph,
        "red2_image": components.red2_image,
        "red2_diamond_separator": components.red2_diamond_separator,
        "red2_credits": components.red2_credits,
        # 红色模板3
        "red3_top_decoration": components.red3_top_decoration,
        "red3_card_with_corner_open": components.red3_card_with_corner_open,
        "red3_card_with_corner_close": components.red3_card_with_corner_close,
        "red3_separator_bar": components.red3_separator_bar,
        "red3_content_card_open": components.red3_content_card_open,
        "red3_content_card_close": components.red3_content_card_close,
        "red3_paragraph": components.red3_paragraph,
        "red3_paragraph_spacing": components.red3_paragraph_spacing,
        "red3_image": components.red3_image,
        "red3_halfcircle_row": components.red3_halfcircle_row,
        "red3_end_marker": components.red3_end_marker,
        "red3_credits": components.red3_credits,
        # 紫色模板
        "purple_heading": components.purple_heading,
        "purple_text_block": components.purple_text_block,
        "purple_image": components.purple_image,
        "purple_separator": components.purple_separator,
        "purple_credits": components.purple_credits,
    })

    # 确定使用的模板
    if template_name:
        tpl_name = template_name
    elif category == "lecture":
        tpl_name = "lecture"
    else:
        tpl_name = "news"

    if tpl_name == "lecture":
        template = env.get_template("lecture.html")
        # 提取讲座数据
        lectures = data.get("lectures", None)
        if lectures is None:
            lectures = _prepare_lectures(sections, images_dir)
        else:
            for lec in lectures:
                if lec.get("poster"):
                    lec["poster"] = _resolve_image_path(lec["poster"], images_dir)
                if lec.get("photo"):
                    lec["photo"] = _resolve_image_path(lec["photo"], images_dir)

        # 讲座模板必须有署名，缺失时使用默认占位符
        if not credits.get("美编"):
            credits.setdefault("美编", [LECTURE_DEFAULT_CREDIT])
        if not credits.get("责编"):
            credits.setdefault("责编", [LECTURE_DEFAULT_CREDIT])

        html = template.render(
            lectures=lectures,
            credits=credits,
            head_img_html=head_img_html,
            tail_img_html=tail_img_html,
        )
    else:
        # news / news_blue2 / interview 等非讲座模板
        template = env.get_template(f"{tpl_name}.html")
        emphasis_color = TEMPLATE_EMPHASIS_COLOR.get(tpl_name)
        prepared_sections = _prepare_news_sections(sections, images_dir, emphasis_color=emphasis_color)

        html = template.render(
            sections=prepared_sections,
            credits=credits,
            title=title,
            head_img_html=head_img_html,
            tail_img_html=tail_img_html,
        )

    return html
