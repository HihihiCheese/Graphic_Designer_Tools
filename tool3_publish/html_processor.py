"""
tool3_publish/html_processor.py - HTML 处理模块

将 tool2 输出的 layout.html 处理为可复制粘贴到公众号的格式：
1. 提取 <body> 内容
2. 将本地 file:/// 图片上传到图床，替换为公开URL
3. 保留 https:// CDN 图片不动（秀米装饰图等）
4. 更新署名文本（责编/美编）
"""

import re
import tempfile
from pathlib import Path
from urllib.parse import unquote

import requests


def process_html_for_publish(html_path, image_host=None, dry_run=False):
    """主函数：读取 layout.html，上传图片并替换 URL

    Args:
        html_path: layout.html 文件路径
        image_host: SMImageHost 实例（用于上传图片）
        dry_run: 模拟运行，不实际上传

    Returns:
        tuple: (processed_html, local_image_paths)
            - processed_html: 处理后的正文 HTML 片段
            - local_image_paths: 本地图片路径列表
    """
    html_path = Path(html_path)
    with open(html_path, "r", encoding="utf-8") as f:
        full_html = f.read()

    # 提取 <body> 内容（微信编辑器只要正文片段）
    body_html = _extract_body(full_html)

    # 找出所有本地图片路径
    local_images = _find_local_images(body_html)

    if not local_images:
        print("  未找到本地图片，跳过上传")
        return body_html, []

    print(f"  找到 {len(local_images)} 张本地图片")

    # 逐张上传并替换
    local_image_paths = []
    for i, (original_url, local_path) in enumerate(local_images, 1):
        local_path_obj = Path(local_path)
        local_image_paths.append(local_path)

        if not local_path_obj.exists():
            print(f"  [{i}/{len(local_images)}] 跳过（文件不存在）: {local_path_obj.name}")
            continue

        if dry_run:
            print(f"  [{i}/{len(local_images)}] [模拟] 上传: {local_path_obj.name}")
            body_html = body_html.replace(
                original_url,
                f"https://placeholder.example.com/{local_path_obj.name}",
            )
        else:
            print(f"  [{i}/{len(local_images)}] 上传: {local_path_obj.name}")
            try:
                public_url = image_host.upload(local_path)
                body_html = body_html.replace(original_url, public_url)
                print(f"       → {public_url[:60]}...")
            except Exception as e:
                print(f"       上传失败: {e}")

    # 上传外部 CDN 素材图片（秀米装饰图、头尾图等）
    cdn_images = _find_cdn_images(body_html)
    if cdn_images:
        print(f"\n  找到 {len(cdn_images)} 张外部素材图片，一并上传...")
        for i, cdn_url in enumerate(cdn_images, 1):
            if dry_run:
                print(f"  [{i}/{len(cdn_images)}] [模拟] 素材: {cdn_url[-40:]}")
            else:
                print(f"  [{i}/{len(cdn_images)}] 素材: ...{cdn_url[-40:]}")
                try:
                    public_url = _download_and_upload(cdn_url, image_host)
                    body_html = body_html.replace(cdn_url, public_url)
                    print(f"       → {public_url[:60]}...")
                except Exception as e:
                    print(f"       上传失败，保留原URL: {e}")
                import time
                time.sleep(1)

    return body_html, local_image_paths


def _find_cdn_images(html):
    """找出 HTML 中所有外部 CDN 图片 URL（秀米素材等）

    排除已上传到图床的 URL（ibb.co、smms 等）。

    Returns:
        list[str]: 去重后的外部图片 URL 列表
    """
    # 已知图床域名，跳过不再重复上传
    SKIP_DOMAINS = ["i.ibb.co", "ibb.co", "imgbb.com", "smms.app", "sm.ms",
                    "placeholder.example.com"]
    pattern = r'src="(https?://[^"]+\.(?:gif|png|jpg|jpeg))"'
    urls = []
    seen = set()
    for match in re.finditer(pattern, html, re.IGNORECASE):
        url = match.group(1)
        if url in seen:
            continue
        if any(domain in url for domain in SKIP_DOMAINS):
            continue
        seen.add(url)
        urls.append(url)
    return urls


def _download_and_upload(url, image_host):
    """下载外部图片到临时文件，上传到图床

    Args:
        url: 外部图片 URL
        image_host: 图床客户端实例

    Returns:
        str: 上传后的公开 URL
    """
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    # 从 URL 推断扩展名
    ext = ".gif"
    for e in [".png", ".jpg", ".jpeg", ".gif"]:
        if e in url.lower():
            ext = e
            break

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(resp.content)
        tmp_path = tmp.name

    try:
        return image_host.upload(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def update_credits_in_html(html, credits):
    """更新 HTML 中的署名文本

    所有模板的署名格式统一为 '{role} | {names}' 在 <span> 内，
    直接用正则替换名字部分。

    Args:
        html: 正文 HTML
        credits: {"责编": "新名字", "美编": "新名字"} — 要更新的署名

    Returns:
        str: 更新后的 HTML
    """
    for role, new_name in credits.items():
        if not new_name:
            continue
        # 匹配 "责编 | 旧名字" 或 "美编 | 旧名字"（中英文竖线都匹配）
        # 替换 | 后面到 </span> 或 </p> 前的内容
        pattern = rf'({re.escape(role)}\s*[|｜]\s*).+?(?=</)'
        replacement = rf'\g<1>{new_name}'
        html = re.sub(pattern, replacement, html)
    return html


def extract_credits_from_html(html):
    """从 HTML 中提取当前署名信息

    Args:
        html: HTML 内容

    Returns:
        dict: {"责编": "名字", "美编": "名字", ...}
    """
    credits = {}
    # 匹配 "角色 | 名字" 模式
    pattern = r'([\u4e00-\u9fff]+)\s*[|｜]\s*(.+?)(?=<)'
    for match in re.finditer(pattern, html):
        role = match.group(1).strip()
        name = match.group(2).strip()
        credits[role] = name
    return credits


def _extract_body(html):
    """提取 <body> 标签内的内容"""
    match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    if match:
        return match.group(1).strip()
    return html


def _find_local_images(html):
    """找出 HTML 中所有 file:/// 本地图片

    Returns:
        list[tuple[str, str]]: [(原始URL, 本地文件路径), ...]
    """
    results = []
    pattern = r'src="(file:///[^"]+)"'
    for match in re.finditer(pattern, html):
        file_url = match.group(1)
        local_path = _decode_file_url(file_url)
        results.append((file_url, local_path))
    return results


def _decode_file_url(url):
    """将 file:/// URL 解码为本地路径

    处理 URL 编码的中文路径，如:
    file:///D:/%E5%BA%94%E7%94%A8/... → D:\\应用\\...
    """
    if url.startswith("file:///"):
        path_part = url[len("file:///"):]
    elif url.startswith("file://"):
        path_part = url[len("file://"):]
    else:
        return url

    # URL 解码（处理 %E5%BA%94 这样的编码）
    decoded = unquote(path_part)
    # Windows 路径：将 / 转为 \
    decoded = decoded.replace("/", "\\")
    return decoded
