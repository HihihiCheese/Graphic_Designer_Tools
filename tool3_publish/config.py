"""
tool3_publish/config.py - 配置管理

管理两部分配置：
1. 图床配置（必需）— SM.MS API Token，用于上传图片
2. 公众号 API 配置（可选）— 备用，等有管理员权限后启用
"""

import json
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent

# 配置文件路径
CONFIG_PATH = ROOT_DIR / "config.json"
CONFIG_EXAMPLE_PATH = ROOT_DIR / "config.example.json"


def load_config():
    """读取 config.json 配置文件

    Returns:
        dict: 完整配置字典

    Raises:
        SystemExit: 配置文件不存在时，打印引导信息后退出
    """
    if not CONFIG_PATH.exists():
        print("错误: 未找到 config.json 配置文件！", file=sys.stderr)
        print()
        print_setup_guide()
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config


def get_image_hosting_config():
    """获取图床配置（provider + token/api_key）

    Returns:
        tuple: (provider, token)  provider 为 "smms" 或 "imgbb"

    Raises:
        SystemExit: 未配置时退出
    """
    config = load_config()
    hosting = config.get("image_hosting", {})
    provider = hosting.get("provider", "smms")
    token = hosting.get("token", "")

    if not token:
        print("错误: 图床 API Token 未配置！", file=sys.stderr)
        print()
        print("请在 config.json 中配置图床:", file=sys.stderr)
        print()
        print("  方案A — ImgBB（推荐，免费32MB）:", file=sys.stderr)
        print('    "image_hosting": {', file=sys.stderr)
        print('      "provider": "imgbb",', file=sys.stderr)
        print('      "token": "你的API Key"', file=sys.stderr)
        print("    }", file=sys.stderr)
        print("  获取: https://api.imgbb.com/ → Get API key", file=sys.stderr)
        print()
        print("  方案B — SM.MS（免费5MB）:", file=sys.stderr)
        print('    "image_hosting": {', file=sys.stderr)
        print('      "provider": "smms",', file=sys.stderr)
        print('      "token": "你的token"', file=sys.stderr)
        print("    }", file=sys.stderr)
        print("  获取: https://smms.app/home/apitoken", file=sys.stderr)
        sys.exit(1)

    return provider, token


def get_image_hosting_token():
    """兼容旧接口，返回 token"""
    _, token = get_image_hosting_config()
    return token


def get_account(key):
    """获取指定公众号账号的配置（备用，API模式）

    Args:
        key: 账号标识（如 "工程管理学院"、"工管青年"）

    Returns:
        dict: {"app_id": "wx...", "app_secret": "...", "name": "南京大学工程管理学院"}
    """
    config = load_config()
    accounts = config.get("accounts", {})

    if key not in accounts:
        print(f"错误: 未找到账号 '{key}'", file=sys.stderr)
        print(f"可用账号: {', '.join(accounts.keys())}", file=sys.stderr)
        sys.exit(1)

    return accounts[key]


def list_accounts():
    """列出所有可用公众号账号

    Returns:
        list[tuple[str, str]]: [(key, display_name), ...]
    """
    config = load_config()
    accounts = config.get("accounts", {})
    return [(key, acc.get("name", key)) for key, acc in accounts.items()]


def print_setup_guide():
    """打印完整的配置引导信息"""
    print("=" * 60)
    print("  工具3 配置指南")
    print("=" * 60)
    print()
    print("【第一步】创建配置文件")
    print(f"  复制模板: config.example.json → config.json")
    print()
    print("【第二步】配置 SM.MS 图床（必需）")
    print("  图片需要上传到图床，复制粘贴到公众号时才能正常显示。")
    print("  1. 注册 SM.MS: https://smms.app")
    print("  2. 登录后访问: https://smms.app/home/apitoken")
    print("  3. 点击 Generate Secret Token")
    print("  4. 将 token 填入 config.json:")
    print('     "image_hosting": { "token": "你的token" }')
    print()
    print("【第三步】配置公众号账号（可选，备用）")
    print("  如果有管理员权限，可配置 API 直接推送草稿：")
    print("  - 登录 https://mp.weixin.qq.com")
    print("  - 设置与开发 → 基本配置 → 获取 AppID/AppSecret")
    print("  - 填入 config.json 的 accounts 字段")
    print()
    print(f"  模板位置: {CONFIG_EXAMPLE_PATH}")
    print(f"  配置位置: {CONFIG_PATH}")
    print()
    print("【注意】")
    print("  - config.json 已加入 .gitignore，不会提交到 Git")
    print("  - SM.MS 免费账户单张图片限制 5MB，超过会自动压缩")
    print("=" * 60)
