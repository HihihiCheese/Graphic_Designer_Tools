"""
tool1_extract/main.py - 内容提取工具 CLI 入口

用法:
    python -m tool1_extract.main <docx路径> [选项]

选项:
    --output-dir DIR    输出目录（默认: output/<文档名>/）
    --no-llm            跳过 LLM 处理，仅做规则提取
    --provider NAME     LLM 提供者: claude(默认) 或 gemini
    --fallback          LLM 失败时使用回退规则（默认开启）

输出:
    output/<文档名>/extracted.json   结构化 JSON
    output/<文档名>/images/          提取的图片
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tool1_extract.docx_parser import parse_docx
from tool1_extract.llm_processor import process_with_llm, _fallback_process


def main():
    parser = argparse.ArgumentParser(
        description="从 Word 文档中提取结构化内容和图片"
    )
    parser.add_argument("docx_path", help="Word 文档路径")
    parser.add_argument("--output-dir", default=None, help="输出目录")
    parser.add_argument("--no-llm", action="store_true", help="跳过 LLM，仅用规则处理")
    parser.add_argument("--provider", default="claude", choices=["claude", "gemini"],
                        help="LLM 提供者（默认 claude）")
    args = parser.parse_args()

    docx_path = Path(args.docx_path)
    if not docx_path.exists():
        print(f"错误: 文件不存在 - {docx_path}", file=sys.stderr)
        sys.exit(1)

    # 确定输出目录
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path("output") / docx_path.stem

    print(f"[1/3] 解析文档: {docx_path.name}")

    # Step 1: 解析 Word 文档
    parse_result = parse_docx(str(docx_path), output_dir=str(output_dir))

    print(f"      提取了 {parse_result['paragraph_count']} 个段落, "
          f"{parse_result['image_count']} 张图片")

    # 保存原始解析结果
    raw_json_path = output_dir / "raw_paragraphs.json"
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(parse_result, f, ensure_ascii=False, indent=2)
    print(f"      原始数据已保存: {raw_json_path}")

    # Step 2: LLM 处理或回退规则
    if args.no_llm:
        print(f"[2/3] 使用规则处理（--no-llm）")
        structured = _fallback_process(parse_result["raw_paragraphs"])
    else:
        print(f"[2/3] 调用 {args.provider} 进行智能处理...")
        structured = process_with_llm(parse_result["raw_paragraphs"], provider=args.provider)

    # 补充元数据
    structured["source_file"] = parse_result["source_file"]
    structured["images_dir"] = parse_result["images_dir"]
    structured["image_count"] = parse_result["image_count"]

    # 标题为空时，用文件名（去掉扩展名）作为标题
    if not structured.get("title"):
        structured["title"] = docx_path.stem
        print(f"      标题从文件名推断: {structured['title']}")

    # Step 3: 保存结构化结果
    output_json_path = output_dir / "extracted.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)

    print(f"[3/3] 结构化结果已保存: {output_json_path}")
    print()
    print(f"=== 提取完成 ===")
    print(f"标题: {structured.get('title', '未知')}")
    print(f"类型: {structured.get('category', '未知')}")
    print(f"摘要: {structured.get('summary', '无')[:80]}...")
    credits = structured.get("credits", {})
    if credits:
        credits_str = "  ".join(f"{k}: {', '.join(v)}" for k, v in credits.items())
    else:
        credits_str = "无"
    print(f"署名: {credits_str}")
    print(f"内容块数: {len(structured.get('sections', []))}")
    print(f"图片数: {parse_result['image_count']}")
    print(f"输出目录: {output_dir}")


if __name__ == "__main__":
    main()
