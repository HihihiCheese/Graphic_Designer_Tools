"""
tool3_publish/wechat_api.py - 微信公众号 API 客户端

封装微信公众号草稿推送所需的全部接口：
- access_token 获取与缓存
- 文章内图片上传 (uploadimg)
- 封面图上传 (永久素材 add_material)
- 创建草稿 (draft/add)
"""

import json
import time
from pathlib import Path

import requests

# 微信 API 基础地址
BASE_URL = "https://api.weixin.qq.com"

# 图片大小上限（10MB），超过则压缩
IMAGE_MAX_SIZE = 10 * 1024 * 1024

# 常见错误码 → 中文提示
ERROR_MESSAGES = {
    -1: "系统繁忙，请稍后重试",
    40001: "AppSecret 错误或 access_token 无效，请检查配置",
    40002: "不合法的凭证类型",
    40014: "access_token 不合法，请重新获取",
    40125: "AppSecret 不正确，请在公众号后台重新获取",
    40164: "IP 不在白名单中，请在公众号后台 → 基本配置 → IP白名单 中添加当前IP",
    41001: "缺少 access_token 参数",
    42001: "access_token 已过期，正在自动刷新",
    45009: "接口调用超过限制，请明天再试",
    48001: "接口权限不足，请确认公众号已认证且开通了对应接口权限",
    50002: "用户受限，无法调用该接口",
}

# 需要自动重试的错误码（token 过期相关）
TOKEN_EXPIRED_CODES = {40014, 42001}


class WeChatAPIError(Exception):
    """微信 API 调用异常"""

    def __init__(self, errcode, errmsg):
        self.errcode = errcode
        self.errmsg = errmsg
        # 优先使用中文提示
        hint = ERROR_MESSAGES.get(errcode, "")
        if hint:
            super().__init__(f"微信API错误 [{errcode}]: {hint} (原始: {errmsg})")
        else:
            super().__init__(f"微信API错误 [{errcode}]: {errmsg}")


class WeChatClient:
    """微信公众号 API 客户端

    每个实例对应一个公众号账号。

    Args:
        app_id: 公众号 AppID
        app_secret: 公众号 AppSecret
        name: 公众号名称（用于日志输出）
    """

    def __init__(self, app_id, app_secret, name=""):
        self.app_id = app_id
        self.app_secret = app_secret
        self.name = name
        self._access_token = None
        self._token_expires_at = 0  # token 过期时间戳

    def get_access_token(self, force_refresh=False):
        """获取 access_token，带缓存（2小时有效期，提前5分钟刷新）

        Args:
            force_refresh: 强制刷新 token

        Returns:
            str: access_token
        """
        # 如果 token 未过期且不强制刷新，直接返回缓存
        if not force_refresh and self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        url = f"{BASE_URL}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret,
        }

        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise WeChatAPIError(data["errcode"], data.get("errmsg", ""))

        self._access_token = data["access_token"]
        # 提前 5 分钟刷新（官方有效期 7200 秒）
        self._token_expires_at = time.time() + data.get("expires_in", 7200) - 300
        return self._access_token

    def _request(self, method, path, retry_on_token_error=True, **kwargs):
        """带自动 token 刷新的请求封装

        Args:
            method: HTTP 方法 ("GET" / "POST")
            path: API 路径（如 "/cgi-bin/draft/add"）
            retry_on_token_error: 遇到 token 过期是否自动刷新重试
            **kwargs: 传给 requests 的参数

        Returns:
            dict: API 返回的 JSON 数据
        """
        token = self.get_access_token()
        url = f"{BASE_URL}{path}?access_token={token}"

        resp = requests.request(method, url, timeout=30, **kwargs)
        data = resp.json()

        errcode = data.get("errcode", 0)

        # token 过期，自动刷新重试一次
        if errcode in TOKEN_EXPIRED_CODES and retry_on_token_error:
            token = self.get_access_token(force_refresh=True)
            url = f"{BASE_URL}{path}?access_token={token}"
            resp = requests.request(method, url, timeout=30, **kwargs)
            data = resp.json()
            errcode = data.get("errcode", 0)

        if errcode != 0:
            raise WeChatAPIError(errcode, data.get("errmsg", ""))

        return data

    def upload_article_image(self, image_path):
        """上传文章内图片（用于正文中的 <img> 标签）

        使用 uploadimg 接口，返回微信 CDN URL。
        图片超过 10MB 会自动压缩。

        Args:
            image_path: 本地图片路径

        Returns:
            str: 微信图片 URL（如 https://mmbiz.qpic.cn/...）
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片不存在: {image_path}")

        # 检查大小，超限则压缩
        actual_path = self._maybe_compress(image_path)

        with open(actual_path, "rb") as f:
            files = {"media": (image_path.name, f, self._guess_mime(image_path))}
            data = self._request("POST", "/cgi-bin/media/uploadimg", files=files)

        return data["url"]

    def upload_cover_image(self, image_path):
        """上传封面图（永久图片素材）

        使用 add_material 接口，返回 media_id 用于草稿封面。

        Args:
            image_path: 本地图片路径

        Returns:
            str: 封面图的 media_id
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"封面图不存在: {image_path}")

        actual_path = self._maybe_compress(image_path)

        with open(actual_path, "rb") as f:
            files = {"media": (image_path.name, f, self._guess_mime(image_path))}
            data = self._request(
                "POST",
                "/cgi-bin/material/add_material",
                files=files,
                data={"type": "image"},
            )

        return data["media_id"]

    def create_draft(self, title, content, cover_media_id, digest="", author=""):
        """创建公众号草稿

        Args:
            title: 文章标题
            content: 正文 HTML（已替换为微信图片URL）
            cover_media_id: 封面图 media_id
            digest: 文章摘要（为空则自动截取正文前54字）
            author: 作者名

        Returns:
            str: 草稿的 media_id
        """
        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "thumb_media_id": cover_media_id,
            "need_open_comment": 0,  # 不开启评论
            "only_fans_can_comment": 0,
        }

        payload = {"articles": [article]}
        data = self._request(
            "POST",
            "/cgi-bin/draft/add",
            json=payload,
        )

        return data["media_id"]

    def _maybe_compress(self, image_path):
        """如果图片超过 10MB，使用 Pillow 压缩

        Args:
            image_path: 原始图片路径

        Returns:
            Path: 原始路径（未超限）或压缩后的临时路径
        """
        image_path = Path(image_path)
        if image_path.stat().st_size <= IMAGE_MAX_SIZE:
            return image_path

        try:
            from PIL import Image
        except ImportError:
            print("  警告: 图片超过10MB但未安装 Pillow，跳过压缩，上传可能失败")
            return image_path

        print(f"  图片超过10MB，正在压缩: {image_path.name}")
        img = Image.open(image_path)

        # 等比缩小到 2000px 宽度
        if img.width > 2000:
            ratio = 2000 / img.width
            new_size = (2000, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 保存为压缩后的 JPEG
        compressed_path = image_path.parent / f"_compressed_{image_path.stem}.jpg"
        img.convert("RGB").save(compressed_path, "JPEG", quality=85, optimize=True)
        print(f"  压缩完成: {compressed_path.stat().st_size / 1024 / 1024:.1f}MB")
        return compressed_path

    @staticmethod
    def _guess_mime(path):
        """根据后缀猜测 MIME 类型"""
        suffix = Path(path).suffix.lower()
        return {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }.get(suffix, "image/jpeg")
