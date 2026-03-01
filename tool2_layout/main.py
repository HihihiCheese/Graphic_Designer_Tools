"""
tool2_layout/main.py - 排版生成工具 CLI 入口

用法:
    python -m tool2_layout.main <extracted_json_path> [选项]

选项:
    --head-img PATH     自定义头图路径
    --tail-img PATH     自定义尾图路径
    --no-preview        不自动打开浏览器预览

输出:
    output/<文章名>/layout.html
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tool2_layout.renderer import render


def main():
    parser = argparse.ArgumentParser(
        description="将 extracted.json 渲染为微信公众号兼容的 HTML"
    )
    parser.add_argument("json_path", help="extracted.json 文件路径")
    parser.add_argument("--head-img", default=None, help="自定义头图路径")
    parser.add_argument("--tail-img", default=None, help="自定义尾图路径")
    parser.add_argument("--template", default=None,
                        choices=["news", "news_blue2", "news_red", "news_red2", "news_cyan", "news_purple", "lecture"],
                        help="指定模板（默认根据 category 自动选择）")
    parser.add_argument("--no-preview", action="store_true", help="不自动打开浏览器预览")
    args = parser.parse_args()

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"错误: 文件不存在 - {json_path}", file=sys.stderr)
        sys.exit(1)

    # 读取 JSON 获取标题信息
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "未命名")
    category = data.get("category", "news")
    section_count = len(data.get("sections", []))

    tpl_display = args.template or ("lecture" if category == "lecture" else "news(自动)")
    print(f"[tool2] 排版生成工具")
    print(f"  标题: {title}")
    print(f"  类型: {category}")
    print(f"  模板: {tpl_display}")
    print(f"  内容块: {section_count}")
    print()

    # 渲染
    print(f"[1/2] 渲染 HTML...")
    html = render(
        str(json_path),
        head_img=args.head_img,
        tail_img=args.tail_img,
        template_name=args.template,
    )

    # 输出路径：与 extracted.json 同目录
    output_path = json_path.parent / "layout.html"

    # 包裹完整 HTML 文档结构（用于本地预览）
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{
    max-width: 600px;
    margin: 0 auto;
    padding: 20px 0;
    background: #f5f5f5;
    font-family: 微软雅黑, sans-serif;
  }}
</style>
</head>
<body>
{html}
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"[2/2] HTML 已保存: {output_path}")
    print()
    print(f"=== 排版完成 ===")
    print(f"输出文件: {output_path}")

    # 自动预览（Windows 用 os.startfile，兼容含空格/中文的路径）
    if not args.no_preview:
        print(f"正在打开浏览器预览...")
        os.startfile(str(output_path.resolve()))


if __name__ == "__main__":
    main()
