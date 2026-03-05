"""
tool3_publish/main.py - 公众号草稿推送助手 CLI 入口

将 tool2 输出的 layout.html 处理为可复制粘贴到公众号后台的格式：
1. 交互确认署名（责编、美编）
2. 上传本地图片到图床，替换为公开URL
3. 生成「推送助手」页面（标题/摘要/正文分区，带一键复制按钮）
4. 浏览器打开，用户复制粘贴到公众号后台即可

用法:
    python -m tool3_publish.main <article_dir> [选项]

选项:
    --setup           仅打印配置引导信息
    --dry-run         模拟运行，不实际上传图片
    --no-preview      不自动打开浏览器

示例:
    python -m tool3_publish.main output/稿件名/
    python -m tool3_publish.main output/稿件名/ --dry-run
    python -m tool3_publish.main --setup
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tool3_publish.config import get_image_hosting_config, get_image_hosting_token, load_config, print_setup_guide
from tool3_publish.html_processor import (
    extract_credits_from_html,
    process_html_for_publish,
    update_credits_in_html,
    _extract_body,
    _find_local_images,
)
from tool3_publish.image_hosting import SMImageHost, ImgbbImageHost, ImageHostError


def _load_article_info(article_dir):
    """加载文章信息（从 extracted.json 和 layout.html）

    Returns:
        dict: {title, category, summary, credits_html, html_path, json_path, image_count}
    """
    article_dir = Path(article_dir)

    html_path = article_dir / "layout.html"
    if not html_path.exists():
        print(f"错误: 未找到 layout.html: {html_path}", file=sys.stderr)
        print("请先运行 tool2 生成排版文件", file=sys.stderr)
        sys.exit(1)

    # 从 extracted.json 读取标题和摘要
    json_path = article_dir / "extracted.json"
    title = "未命名"
    category = "news"
    summary = ""

    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        title = data.get("title", "未命名")
        category = data.get("category", "news")
        summary = data.get("summary", "")

    # 从 HTML 中提取署名
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    body_html = _extract_body(html_content)
    credits_html = extract_credits_from_html(body_html)
    local_images = _find_local_images(body_html)

    return {
        "title": title,
        "category": category,
        "summary": summary,
        "credits_html": credits_html,
        "html_path": html_path,
        "json_path": json_path,
        "image_count": len(local_images),
    }


def _phase1_show_info(info):
    """[阶段1] 显示文章信息"""
    print()
    print("=" * 50)
    print("  [tool3] 公众号推送助手")
    print("=" * 50)
    print()
    print(f"  标题: {info['title']}")
    print(f"  类型: {info['category']}")
    print(f"  摘要: {info['summary'][:40]}..." if len(info['summary']) > 40 else f"  摘要: {info['summary'] or '（无）'}")
    print(f"  本地图片: {info['image_count']} 张")
    print(f"  排版文件: {info['html_path']}")
    print()


def _phase2_confirm_credits(info):
    """[阶段2] 署名确认

    显示当前所有署名，逐一确认责编和美编。
    回车保持原值，输入新内容则修改。
    责编/美编为空时强制要求输入。

    Returns:
        dict: 需要更新的署名 {"责编": "新名字", ...}
    """
    print("-" * 50)
    print("  [阶段2] 署名确认")
    print("-" * 50)

    credits = info["credits_html"]

    if credits:
        print("  当前署名:")
        for role, name in credits.items():
            print(f"    {role}: {name}")
    else:
        print("  当前无署名信息")
    print()

    key_roles = ["责编", "美编"]
    updated = {}

    for role in key_roles:
        current = credits.get(role, "")
        if current:
            user_input = input(f"  {role} [{current}] (回车保持，输入修改): ").strip()
            if user_input:
                updated[role] = user_input
        else:
            while True:
                user_input = input(f"  {role} [未设置，必填]: ").strip()
                if user_input:
                    updated[role] = user_input
                    break
                print(f"  {role}不能为空，请输入")

    # 其他署名角色
    other_roles = [r for r in credits if r not in key_roles]
    if other_roles:
        print()
        for role in other_roles:
            current = credits[role]
            user_input = input(f"  {role} [{current}] (回车保持): ").strip()
            if user_input:
                updated[role] = user_input

    print()
    return updated


def _phase3_confirm(info, updated_credits):
    """[阶段3] 最终确认

    Returns:
        bool: True=确认执行, False=取消
    """
    print("-" * 50)
    print("  [阶段3] 确认")
    print("-" * 50)
    print()
    print(f"  标题:   {info['title']}")

    final_credits = dict(info["credits_html"])
    final_credits.update(updated_credits)
    for role in ["责编", "美编"]:
        name = final_credits.get(role, "未设置")
        mark = " (已修改)" if role in updated_credits else ""
        print(f"  {role}:   {name}{mark}")

    print(f"  图片:   {info['image_count']} 张待上传到图床")
    print()

    while True:
        confirm = input("  确认处理? (y/n): ").strip().lower()
        if confirm in ("y", "yes", ""):
            return True
        if confirm in ("n", "no"):
            return False
        print("  请输入 y 或 n")


def _phase4_process(info, updated_credits, dry_run=False):
    """[阶段4] 执行处理：上传图片 + 生成推送助手页面

    Returns:
        Path: 推送助手页面路径
    """
    print()
    print("-" * 50)
    print("  [阶段4] 处理中" + (" [模拟模式]" if dry_run else ""))
    print("-" * 50)
    print()

    # 创建图床客户端
    image_host = None
    if not dry_run:
        try:
            provider, token = get_image_hosting_config()
            if provider == "imgbb":
                image_host = ImgbbImageHost(token)
                print(f"  图床: ImgBB")
            else:
                image_host = SMImageHost(token)
                print(f"  图床: SM.MS")
        except ImageHostError as e:
            print(f"  错误: {e}", file=sys.stderr)
            sys.exit(1)

    # [1/3] 上传图片并替换URL
    print("[1/3] 上传图片到图床...")
    processed_html, local_image_paths = process_html_for_publish(
        info["html_path"], image_host=image_host, dry_run=dry_run
    )

    # [2/3] 更新署名
    if updated_credits:
        print()
        print("[2/3] 更新署名...")
        processed_html = update_credits_in_html(processed_html, updated_credits)
        for role, name in updated_credits.items():
            print(f"    {role} → {name}")
    else:
        print()
        print("[2/3] 署名无变更")

    # [3/3] 生成推送助手页面
    print()
    print("[3/3] 生成推送助手页面...")
    output_path = info["html_path"].parent / "publish_helper.html"
    helper_html = _build_helper_page(
        title=info["title"],
        summary=info["summary"],
        content_html=processed_html,
    )

    with open(output_path, "w", encoding="utf-8", errors="replace") as f:
        f.write(helper_html)

    print(f"  已保存: {output_path}")
    return output_path


def _build_helper_page(title, summary, content_html):
    """生成推送助手 HTML 页面

    页面包含三个区域：标题、摘要、正文，各带一键复制按钮。
    用户在浏览器中打开此页面，逐项复制粘贴到公众号后台。
    """
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>推送助手 - {title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, "Microsoft YaHei", sans-serif;
    background: #f0f2f5;
    color: #333;
  }}

  /* 顶部导航栏 */
  .navbar {{
    background: #07c160;
    color: white;
    padding: 16px 24px;
    font-size: 18px;
    font-weight: bold;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }}
  .navbar small {{
    font-weight: normal;
    font-size: 13px;
    opacity: 0.85;
    margin-left: 12px;
  }}

  /* 使用说明 */
  .instructions {{
    max-width: 780px;
    margin: 20px auto;
    background: #fffbe6;
    border: 1px solid #ffe58f;
    border-radius: 8px;
    padding: 16px 20px;
    font-size: 14px;
    line-height: 1.8;
  }}
  .instructions strong {{ color: #d48806; }}

  /* 复制区域 */
  .copy-section {{
    max-width: 780px;
    margin: 16px auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    overflow: hidden;
  }}
  .copy-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: #fafafa;
    border-bottom: 1px solid #f0f0f0;
  }}
  .copy-header h3 {{
    font-size: 15px;
    color: #555;
  }}
  .copy-btn {{
    padding: 6px 16px;
    background: #07c160;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background 0.2s;
  }}
  .copy-btn:hover {{ background: #06ad56; }}
  .copy-btn.copied {{
    background: #52c41a;
  }}

  /* 文本内容区 */
  .copy-text {{
    padding: 16px 20px;
    font-size: 15px;
    line-height: 1.6;
    user-select: all;
    cursor: text;
    border: 2px solid transparent;
    transition: border-color 0.2s;
  }}
  .copy-text:hover {{
    border-color: #07c160;
  }}

  /* 正文预览区 */
  .content-preview {{
    max-width: 780px;
    margin: 16px auto 40px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    overflow: hidden;
  }}
  .content-body {{
    padding: 20px;
    max-width: 600px;
    margin: 0 auto;
  }}
  .content-body img {{
    max-width: 100%;
    height: auto;
  }}
</style>
</head>
<body>

<div class="navbar">
  推送助手
  <small>复制下方内容，粘贴到公众号后台</small>
</div>

<div class="instructions">
  <strong>使用步骤：</strong><br>
  1. 点击「复制标题」→ 粘贴到公众号后台的标题框<br>
  2. 点击「复制摘要」→ 粘贴到公众号后台的摘要框<br>
  3. 点击「复制正文」→ 粘贴到公众号后台的正文编辑区<br>
  4. 检查排版效果，确认无误后保存为草稿
</div>

<!-- 标题 -->
<div class="copy-section">
  <div class="copy-header">
    <h3>标题</h3>
    <button class="copy-btn" onclick="copyText('title-content', this)">复制标题</button>
  </div>
  <div class="copy-text" id="title-content">{title}</div>
</div>

<!-- 摘要 -->
<div class="copy-section">
  <div class="copy-header">
    <h3>摘要</h3>
    <button class="copy-btn" onclick="copyText('summary-content', this)">复制摘要</button>
  </div>
  <div class="copy-text" id="summary-content">{summary or "（请手动填写摘要）"}</div>
</div>

<!-- 正文 -->
<div class="content-preview">
  <div class="copy-header">
    <h3>正文预览</h3>
    <button class="copy-btn" onclick="copyRichText('article-content', this)">复制正文</button>
  </div>
  <div class="content-body" id="article-content">
{content_html}
  </div>
</div>

<script>
// 复制纯文本（标题、摘要）
function copyText(elementId, btn) {{
  const el = document.getElementById(elementId);
  const text = el.innerText.trim();
  navigator.clipboard.writeText(text).then(() => {{
    showCopied(btn);
  }}).catch(() => {{
    // 降级方案
    const range = document.createRange();
    range.selectNodeContents(el);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    document.execCommand('copy');
    sel.removeAllRanges();
    showCopied(btn);
  }});
}}

// 复制富文本（正文，保留格式和图片）
function copyRichText(elementId, btn) {{
  const el = document.getElementById(elementId);

  // 方案1: 使用 Clipboard API 写入 HTML
  const html = el.innerHTML;
  const text = el.innerText;

  if (navigator.clipboard && navigator.clipboard.write) {{
    const blob = new Blob([html], {{ type: 'text/html' }});
    const textBlob = new Blob([text], {{ type: 'text/plain' }});
    const item = new ClipboardItem({{
      'text/html': blob,
      'text/plain': textBlob,
    }});
    navigator.clipboard.write([item]).then(() => {{
      showCopied(btn);
    }}).catch(() => {{
      fallbackCopy(el, btn);
    }});
  }} else {{
    fallbackCopy(el, btn);
  }}
}}

// 降级复制方案（选中 → execCommand）
function fallbackCopy(el, btn) {{
  const range = document.createRange();
  range.selectNodeContents(el);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  document.execCommand('copy');
  sel.removeAllRanges();
  showCopied(btn);
}}

// 按钮反馈
function showCopied(btn) {{
  const originalText = btn.innerText;
  btn.innerText = '已复制!';
  btn.classList.add('copied');
  setTimeout(() => {{
    btn.innerText = originalText;
    btn.classList.remove('copied');
  }}, 1500);
}}
</script>

</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(
        description="将排版好的 HTML 处理为可复制粘贴到公众号后台的格式"
    )
    parser.add_argument(
        "article_dir",
        nargs="?",
        help="文章输出目录（含 layout.html 和 extracted.json）",
    )
    parser.add_argument("--setup", action="store_true", help="仅打印配置引导信息")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际上传图片")
    parser.add_argument("--no-preview", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args()

    # --setup 模式
    if args.setup:
        print_setup_guide()
        return

    if not args.article_dir:
        parser.print_help()
        print()
        print("错误: 请指定文章输出目录", file=sys.stderr)
        print("示例: python -m tool3_publish.main output/稿件名/", file=sys.stderr)
        sys.exit(1)

    article_dir = Path(args.article_dir)
    if not article_dir.is_dir():
        print(f"错误: 目录不存在 - {article_dir}", file=sys.stderr)
        sys.exit(1)

    # 非 dry-run 模式下，先检查配置
    if not args.dry_run:
        load_config()

    # [阶段1] 显示文章信息
    info = _load_article_info(article_dir)
    _phase1_show_info(info)

    # [阶段2] 署名确认
    updated_credits = _phase2_confirm_credits(info)

    # [阶段3] 确认
    confirmed = _phase3_confirm(info, updated_credits)

    if not confirmed:
        print()
        print("  已取消。")
        return

    # [阶段4] 处理并生成推送助手页面
    output_path = _phase4_process(
        info, updated_credits, dry_run=args.dry_run
    )

    # 完成
    print()
    print("=" * 50)
    print("  处理完成！" + (" [模拟模式]" if args.dry_run else ""))
    print("=" * 50)
    print()
    print(f"  推送助手页面: {output_path}")
    print()
    print("  接下来:")
    print("  1. 在浏览器中打开推送助手页面")
    print("  2. 逐项复制「标题」「摘要」「正文」")
    print("  3. 粘贴到公众号后台编辑器")
    print("  4. 检查排版 → 保存草稿 → 审核发布")
    print()

    # 自动打开浏览器
    if not args.no_preview:
        print("正在打开浏览器...")
        os.startfile(str(output_path.resolve()))


if __name__ == "__main__":
    main()
