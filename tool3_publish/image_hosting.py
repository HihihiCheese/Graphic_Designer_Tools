"""
tool3_publish/image_hosting.py - 图床上传模块

将本地图片上传到免费图床，获取公开可访问的 URL。
支持 ImgBB 和 SM.MS 两种图床。
用于替换 HTML 中的 file:/// 本地路径，使复制粘贴到公众号时图片自动带入。
"""

import base64
import os
import time
from pathlib import Path

import requests

# SM.MS 图床 API 地址（国内用 smms.app 更稳定）
SMMS_API_URL = "https://smms.app/api/v2"

# SM.MS 单文件大小限制（5MB）
SMMS_MAX_SIZE = 5 * 1024 * 1024

# ImgBB API 地址
IMGBB_API_URL = "https://api.imgbb.com/1/upload"

# ImgBB 单文件大小限制（32MB）
IMGBB_MAX_SIZE = 32 * 1024 * 1024

# 批量上传间隔（秒），避免触发频率限制
UPLOAD_INTERVAL = 1.0


class ImageHostError(Exception):
    """图床上传异常"""
    pass


class SMImageHost:
    """SM.MS 图床客户端

    Args:
        token: SM.MS API Token（从 https://smms.app/home/apitoken 获取）
    """

    def __init__(self, token):
        if not token:
            raise ImageHostError(
                "SM.MS API Token 未配置！\n"
                "获取方式:\n"
                "  1. 注册 https://smms.app\n"
                "  2. 登录后访问 https://smms.app/home/apitoken\n"
                "  3. 点击 Generate Secret Token\n"
                "  4. 将 token 填入 config.json 的 image_hosting.token 字段"
            )
        self.token = token
        self.session = requests.Session()
        self.session.headers["Authorization"] = token

    def upload(self, image_path):
        """上传单张图片到 SM.MS

        Args:
            image_path: 本地图片路径

        Returns:
            str: 图片的公开访问 URL
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片不存在: {image_path}")

        # 超过 5MB 则压缩
        actual_path = self._maybe_compress(image_path)

        with open(actual_path, "rb") as f:
            files = {"smfile": (image_path.name, f)}
            resp = self.session.post(
                f"{SMMS_API_URL}/upload",
                files=files,
                timeout=30,
            )

        result = resp.json()

        if result.get("success"):
            return result["data"]["url"]

        # 图片已存在，从 message 中提取 URL
        if result.get("code") == "image_repeated":
            msg = result.get("message", "")
            if "at: " in msg:
                return msg.split("at: ")[-1].strip()
            raise ImageHostError(f"图片重复但无法提取URL: {msg}")

        # 其他错误
        raise ImageHostError(
            f"SM.MS 上传失败 [{result.get('code', 'unknown')}]: "
            f"{result.get('message', '未知错误')}"
        )

    def upload_batch(self, image_paths, progress_callback=None):
        """批量上传图片

        Args:
            image_paths: 图片路径列表
            progress_callback: 进度回调 fn(index, total, filename, url_or_error)

        Returns:
            dict: {原始路径: 公开URL} 映射
        """
        url_map = {}
        total = len(image_paths)

        for i, path in enumerate(image_paths):
            path = Path(path)
            try:
                url = self.upload(path)
                url_map[str(path)] = url
                if progress_callback:
                    progress_callback(i + 1, total, path.name, url)
            except Exception as e:
                if progress_callback:
                    progress_callback(i + 1, total, path.name, f"失败: {e}")

            # 批量上传间隔，避免触发频率限制
            if i < total - 1:
                time.sleep(UPLOAD_INTERVAL)

        return url_map

    def _maybe_compress(self, image_path):
        """如果图片超过 5MB，使用 Pillow 压缩

        Returns:
            Path: 原始路径或压缩后的临时路径
        """
        image_path = Path(image_path)
        if image_path.stat().st_size <= SMMS_MAX_SIZE:
            return image_path

        try:
            from PIL import Image
        except ImportError:
            raise ImageHostError(
                f"图片 {image_path.name} 超过5MB但未安装 Pillow，无法压缩。\n"
                f"请运行: pip install Pillow"
            )

        print(f"  图片超过5MB，正在压缩: {image_path.name}")
        img = Image.open(image_path)

        # 等比缩小到 2000px 宽度
        if img.width > 2000:
            ratio = 2000 / img.width
            new_size = (2000, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 保存为压缩后的 JPEG
        compressed_path = image_path.parent / f"_compressed_{image_path.stem}.jpg"
        img.convert("RGB").save(compressed_path, "JPEG", quality=85, optimize=True)
        new_size_mb = compressed_path.stat().st_size / 1024 / 1024
        print(f"  压缩完成: {new_size_mb:.1f}MB")
        return compressed_path


class ImgbbImageHost:
    """ImgBB 图床客户端（免费，单张≤32MB）

    Args:
        api_key: ImgBB API Key（从 https://api.imgbb.com/ 获取）
    """

    def __init__(self, api_key):
        if not api_key:
            raise ImageHostError(
                "ImgBB API Key 未配置！\n"
                "获取方式:\n"
                "  1. 登录 https://imgbb.com\n"
                "  2. 访问 https://api.imgbb.com/\n"
                "  3. 点击 Get API key\n"
                "  4. 将 key 填入 config.json 的 image_hosting.token 字段"
            )
        self.api_key = api_key
        self.session = requests.Session()

    def upload(self, image_path):
        """上传单张图片到 ImgBB

        Args:
            image_path: 本地图片路径

        Returns:
            str: 图片的公开访问 URL
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片不存在: {image_path}")

        # 超过 32MB 则压缩
        actual_path = self._maybe_compress(image_path)

        # ImgBB 接受 base64 编码的图片
        with open(actual_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        resp = self.session.post(
            IMGBB_API_URL,
            data={
                "key": self.api_key,
                "image": image_data,
                "name": image_path.stem,
            },
            timeout=30,
        )

        result = resp.json()

        if result.get("success"):
            return result["data"]["url"]

        # 错误处理
        error = result.get("error", {})
        raise ImageHostError(
            f"ImgBB 上传失败 [{error.get('code', 'unknown')}]: "
            f"{error.get('message', '未知错误')}"
        )

    def upload_batch(self, image_paths, progress_callback=None):
        """批量上传图片

        Args:
            image_paths: 图片路径列表
            progress_callback: 进度回调 fn(index, total, filename, url_or_error)

        Returns:
            dict: {原始路径: 公开URL} 映射
        """
        url_map = {}
        total = len(image_paths)

        for i, path in enumerate(image_paths):
            path = Path(path)
            try:
                url = self.upload(path)
                url_map[str(path)] = url
                if progress_callback:
                    progress_callback(i + 1, total, path.name, url)
            except Exception as e:
                if progress_callback:
                    progress_callback(i + 1, total, path.name, f"失败: {e}")

            # 批量上传间隔
            if i < total - 1:
                time.sleep(UPLOAD_INTERVAL)

        return url_map

    def _maybe_compress(self, image_path):
        """如果图片超过 32MB，使用 Pillow 压缩"""
        image_path = Path(image_path)
        if image_path.stat().st_size <= IMGBB_MAX_SIZE:
            return image_path

        try:
            from PIL import Image
        except ImportError:
            raise ImageHostError(
                f"图片 {image_path.name} 超过32MB但未安装 Pillow，无法压缩。\n"
                f"请运行: pip install Pillow"
            )

        print(f"  图片超过32MB，正在压缩: {image_path.name}")
        img = Image.open(image_path)

        if img.width > 2000:
            ratio = 2000 / img.width
            new_size = (2000, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        compressed_path = image_path.parent / f"_compressed_{image_path.stem}.jpg"
        img.convert("RGB").save(compressed_path, "JPEG", quality=85, optimize=True)
        new_size_mb = compressed_path.stat().st_size / 1024 / 1024
        print(f"  压缩完成: {new_size_mb:.1f}MB")
        return compressed_path
