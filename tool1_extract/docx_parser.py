"""
docx_parser.py - Word 文档解析核心模块

功能：将 .docx 文件解析为有序的内容块列表 + 提取所有图片
支持三种段落类型：纯文字、纯图片、文字+图片混合
"""

import os
import re
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def _extract_image_from_blip(blip, doc_part, images_dir, img_counter):
    """从 blip 元素中提取图片并保存到磁盘

    Args:
        blip: XML blip 元素（包含图片引用）
        doc_part: 文档 part（用于查找 relationship）
        images_dir: 图片保存目录
        img_counter: 当前图片计数器

    Returns:
        (文件名, 新计数器) 或 (None, 原计数器)
    """
    embed_id = blip.get(qn("r:embed"))
    if not embed_id:
        return None, img_counter

    try:
        rel = doc_part.rels[embed_id]
        image_blob = rel.target_part.blob
        # 从 content_type 推断扩展名
        content_type = rel.target_part.content_type
        ext_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/bmp": ".bmp",
            "image/webp": ".webp",
            "image/tiff": ".tiff",
        }
        ext = ext_map.get(content_type, ".png")
        filename = f"img_{img_counter:03d}{ext}"
        filepath = os.path.join(images_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_blob)
        return filename, img_counter + 1
    except (KeyError, AttributeError):
        return None, img_counter


def _find_blips_in_element(element):
    """在 XML 元素中查找所有 blip（图片引用）

    同时检查 inline 和 anchor 类型的 drawing 元素
    """
    blips = []
    # 查找所有 drawing 中的 blip
    for blip in element.findall(f".//{qn('a:blip')}"):
        blips.append(blip)
    return blips


def parse_docx(filepath, output_dir=None):
    """解析 Word 文档，提取有序内容块和图片

    Args:
        filepath: .docx 文件路径
        output_dir: 输出目录，默认为 output/<文档名>/

    Returns:
        {
            "source_file": "原始文件名",
            "raw_paragraphs": [
                {"type": "text", "content": "...", "style": "Normal"},
                {"type": "image", "filename": "img_001.jpg"},
                {"type": "text_with_image", "content": "...", "images": ["img_002.jpg"]},
                ...
            ],
            "images_dir": "output/xxx/images/",
            "image_count": 6,
            "paragraph_count": 21
        }
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")

    # 确定输出目录
    if output_dir is None:
        output_dir = Path("output") / filepath.stem
    else:
        output_dir = Path(output_dir)

    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    doc = Document(str(filepath))
    doc_part = doc.part

    raw_paragraphs = []
    img_counter = 1

    for para in doc.paragraphs:
        text = para.text.strip()
        blips = _find_blips_in_element(para._element)

        has_text = bool(text)
        has_images = bool(blips)

        if not has_text and not has_images:
            # 空段落，跳过
            continue

        if has_text and not has_images:
            # 纯文字段落
            raw_paragraphs.append({
                "type": "text",
                "content": text,
                "style": para.style.name if para.style else "Normal",
            })

        elif has_images and not has_text:
            # 纯图片段落（可能有多张图片）
            for blip in blips:
                filename, img_counter = _extract_image_from_blip(
                    blip, doc_part, str(images_dir), img_counter
                )
                if filename:
                    raw_paragraphs.append({
                        "type": "image",
                        "filename": filename,
                    })

        else:
            # 混合段落：文字 + 图片
            # 策略：先记录文字，图片拆分为独立的内容块追加在后面
            image_filenames = []
            for blip in blips:
                filename, img_counter = _extract_image_from_blip(
                    blip, doc_part, str(images_dir), img_counter
                )
                if filename:
                    image_filenames.append(filename)

            if image_filenames:
                raw_paragraphs.append({
                    "type": "text_with_image",
                    "content": text,
                    "images": image_filenames,
                    "style": para.style.name if para.style else "Normal",
                })
            else:
                # blip 提取失败，当作纯文字处理
                raw_paragraphs.append({
                    "type": "text",
                    "content": text,
                    "style": para.style.name if para.style else "Normal",
                })

    result = {
        "source_file": filepath.name,
        "raw_paragraphs": raw_paragraphs,
        "images_dir": str(images_dir),
        "image_count": img_counter - 1,
        "paragraph_count": len(raw_paragraphs),
    }

    return result


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("用法: python docx_parser.py <docx文件路径>")
        sys.exit(1)

    result = parse_docx(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
