# Hicheese Tool - 微信公众号自动化美编工具集

> 南京大学工程管理学院新媒体中心 · 美编自动化工具
>
> 项目作者：**Hicheese** — 南大工管新媒体中心美编

## 项目简介

将微信公众号推文的美编工作从**手动重复劳动**变为**半自动化流水线**。

当前工作流：拿到Word稿件 → 手动在秀米排版 → 手动粘贴到公众号后台 → 审核发布

目标工作流：**拿到Word稿件 → 运行脚本 → 自动生成排版好的推文草稿 → 人工审核发布**

## 核心工具

### 工具1：内容提取与结构化 (`tool1_extract`)

- 输入：Word文档 (.docx)
- 处理：调用 LLM (Claude/Gemini CLI) 自动识别标题、生成摘要、智能分段、分离图片
- 输出：结构化 JSON + 提取的图片文件

### 工具2：模板排版引擎 (`tool2_layout`)

- 输入：工具1输出的结构化 JSON
- 处理：匹配文章类型对应的HTML模板，填充内容，应用美编规范样式
- 输出：符合规范的富文本 HTML 文件

### 工具3：公众号推送助手 (`tool3_publish`)

- 输入：工具2输出的 HTML + 图片素材
- 处理：交互确认署名→上传图片到图床（支持 ImgBB / SM.MS）→生成推送助手页面
- 输出：带一键复制按钮的推送助手页面（标题/摘要/正文分区）
- 特性：本地图片 + 外部 CDN 素材（头尾图、装饰 GIF）全部上传图床，确保复制粘贴后图片正常显示
- 使用方式：浏览器打开 → 逐项复制 → 粘贴到公众号后台

## 美编规范摘要

依据《工程管理学院新媒体部美编规范》：

| 元素 | 规范 |
|------|------|
| 正文 | 14~16px，微软雅黑，两端对齐 |
| 标题 | 16~17px，微软雅黑，加粗，居中 |
| 注解 | 12px，微软雅黑，居中 |
| 行距 | 1.5倍 |
| 缩进 | 无首行缩进 |
| 间距 | 图片与正文之间、段落间加空行；与注解之间不加空行 |
| 图片 | 人像居中，其他自适应屏幕宽度 |

推文类型：学院活动新闻稿 / 采访（含卷首语） / 讲座（统一模板）

## 技术栈

- **语言**：Python 3.11+
- **Word解析**：python-docx
- **LLM调用**：Claude Code CLI / Gemini CLI（本地终端直接调用）
- **模板引擎**：Jinja2
- **公众号API**：微信官方接口 (requests)
- **图片处理**：Pillow

## 开发进度

| Phase | 模块 | 状态 |
|-------|------|------|
| Phase 1 | tool1_extract — 内容提取 | ✅ 已完成 |
| Phase 2 | tool2_layout — 排版生成 | ✅ 已完成 |
| Phase 3 | tool3_publish — 公众号推送 | ✅ 已完成 |
| Phase 4 | pipeline — 全流程串联 | 🔲 待开发 |

## 使用方式

当前为本地个人使用，通过终端命令行调用：

```bash
# 工具1：提取内容（--no-llm 跳过 LLM，仅用规则处理）
python -m tool1_extract.main "稿件.docx"
python -m tool1_extract.main "稿件.docx" --no-llm

# 工具2：生成排版（自动根据 category 选模板，浏览器预览）
python -m tool2_layout.main output/稿件名/extracted.json
python -m tool2_layout.main output/稿件名/extracted.json --template news_purple
# 可选模板: news, news_blue2, news_red, news_red2, news_red3, news_cyan, news_purple, lecture

# 工具3：推送助手（交互确认署名 + 图片上传 + 生成复制页面）
python -m tool3_publish.main output/稿件名/
python -m tool3_publish.main output/稿件名/ --dry-run   # 模拟运行
python -m tool3_publish.main --setup                     # 查看配置指南

# 一键全流程（待开发）
# python pipeline.py input.docx
```

## 项目结构

```
Hicheese_tool/
├── README.md                  # 项目说明
├── PLAN.md                    # 开发计划
├── tool1_extract/             # 工具1：内容提取
│   ├── main.py                # CLI 入口
│   ├── docx_parser.py         # Word文档解析（段落+图片提取）
│   └── llm_processor.py       # LLM智能处理 + 回退规则
├── tool2_layout/              # 工具2：模板排版
│   ├── main.py                # CLI 入口
│   ├── renderer.py            # 渲染引擎：JSON + 模板 → HTML
│   ├── components.py          # 秀米模板 HTML 组件片段（~35个组件）
│   └── templates/
│       ├── news.html          # 蓝色模板1（长新闻稿）
│       ├── news_blue2.html    # 蓝色模板2（短稿）
│       ├── news_red.html      # 红色模板1（党建复杂版）
│       ├── news_red2.html     # 红色模板2（党建简约版）
│       ├── news_red3.html     # 红色模板3（简洁党建/活动短稿）
│       ├── news_cyan.html     # 青色模板（学术论坛）
│       ├── news_purple.html   # 紫色模板（正式通知）
│       └── lecture.html       # 讲座模板
├── tool3_publish/             # 工具3：推送助手
│   ├── main.py                # CLI 入口 + 交互确认 + 生成推送助手页面
│   ├── config.py              # 配置管理（图床token + 公众号API备用）
│   ├── image_hosting.py       # 图床上传（ImgBB / SM.MS）
│   ├── html_processor.py      # HTML 处理（本地+CDN图片上传替换 + 署名更新）
│   └── wechat_api.py          # 微信API客户端（备用，需管理员权限）
├── config.example.json        # 配置模板（复制为 config.json 使用）
├── output/                    # 输出目录
│   ├── clipboard_news.html    # 秀米新闻稿模板源码（参考）
│   ├── clipboard_raw.html     # 秀米讲座模板源码（参考）
│   └── <文章名>/
│       ├── extracted.json     # tool1 输出的结构化 JSON
│       ├── layout.html        # tool2 输出的排版 HTML
│       └── images/            # 提取的图片
├── log/                       # 工作日志
├── docs/                      # 参考文档
│   └── 工程管理学院新媒体美编规范(1).pdf
└── requirements.txt
```
