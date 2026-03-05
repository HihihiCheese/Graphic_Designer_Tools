"""
tool3_publish - 微信公众号推送助手

将 tool2 输出的排版 HTML 处理为可复制粘贴到公众号后台的格式：
- 交互确认署名（责编、美编）
- 上传本地图片到图床（SM.MS），替换为公开URL
- 生成「推送助手」页面，带一键复制按钮
- 浏览器打开，用户复制粘贴到公众号后台即可

用法:
    python -m tool3_publish.main <article_dir> [--dry-run] [--setup]
"""
