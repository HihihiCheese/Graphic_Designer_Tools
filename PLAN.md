# Hicheese Tool - 开发计划

## 设计决策

- **本地优先**：当前仅个人使用，不构建Web界面和API，通过终端命令行调用
- **LLM调用方式**：直接通过 Claude Code CLI / Gemini CLI 在终端调用，无需管理API Key
- **绕过秀米**：不自动操作秀米，而是直接生成符合规范的富文本HTML，通过API推送到公众号后台
- **未来扩展**：如需分享给其他同学，再补充 Streamlit 界面和 API 接口

---

## Phase 0：项目初始化

- [x] 创建项目目录与说明文档
- [x] 初始化 Python 项目（requirements.txt, .gitignore）
- [x] 搭建目录结构骨架（tool1/tool2/tool3 + pipeline）
- [x] 准备测试用的 Word 稿件样本

## Phase 1：工具1 - 内容提取与结构化 ✅ 已完成

### 目标
上传 Word 文档 → 自动输出结构化 JSON + 图片文件

### 任务拆解

#### 1.1 Word 文档解析 (`docx_parser.py`)
- [x] 使用 python-docx 读取 .docx 文件
- [x] 按顺序提取所有段落文本，保留段落层级关系
- [x] 提取文档中的所有图片，按出现顺序编号保存到 output/images/
- [x] 记录图片在文档中的位置（在第几个段落之后）
- [x] 支持纯文字/纯图片/文字+图片混合三种段落类型

#### 1.2 LLM 智能处理 (`llm_processor.py`)
- [x] 将提取的纯文本交给 LLM 处理（Claude CLI / Gemini CLI）
- [x] Prompt 设计：标题识别、类型判断、摘要生成、智能分段、关键词强调
- [x] 通过 subprocess 调用 CLI，stdin 传入避免参数过长
- [x] 回退规则处理（`--no-llm` 模式）：标题/署名/分类的规则推断

#### 1.3 输出格式
- [x] 标准化 JSON 输出：title, summary, category, credits, sections
- [x] 署名智能解析（文字/文编→统一、图片/摄影→统一）
- [x] CLI 入口：`python -m tool1_extract.main <docx> [--no-llm] [--provider claude|gemini]`

### 验收标准 ✅
- 多篇新闻稿 Word 文档均能正确输出结构化 JSON
- 图片完整提取且顺序正确
- `--no-llm` 模式可独立运行

---

## Phase 2：工具2 - 模板排版引擎 ✅ 已完成

### 目标
读取结构化 JSON → 匹配模板 → 输出微信公众号兼容的 HTML

### 核心设计
**不从零写 CSS，而是直接复用秀米模板的 HTML 片段作为 Jinja2 组件**：
- 从秀米剪贴板抓取真实模板 HTML（`clipboard_news.html` / `clipboard_raw.html`）
- 拆分为可复用的 HTML 组件（`components.py`）
- Jinja2 循环 sections，按 type 选择对应组件填入内容
- 装饰元素（条纹PNG、GIF分隔图、阴影样式）原样保留秀米 CDN URL

### 任务拆解

#### 2.1 HTML 组件提取 (`components.py`)
- [x] `text_card` — 新闻稿浅蓝底文字卡片 + 条纹 PNG 边框
- [x] `image_frame` — 白边 + 阴影图片框
- [x] `heading_block` — 加粗居中小节标题
- [x] `news_separator` — 蓝虚线 + 小熊 GIF 分隔
- [x] `credits_block` — 12px 居中署名
- [x] `decorator_line` — 蓝线 + 黄点装饰线（讲座）
- [x] `lecture_info` — 报告人/主持人/时间/地点 信息区
- [x] `lecture_card` — 虚线框内容卡片（讲座）
- [x] `head_image` / `tail_image` — 头尾图 GIF
- [x] `decorator_gif` — 半透明 GIF 段间分隔

#### 2.2 Jinja2 模板
- [x] `templates/news.html` — 新闻稿模板（头图 → 文字卡片/图片交替 → 分隔 → 署名 → 尾图）
- [x] `templates/lecture.html` — 讲座模板（循环N篇讲座，每篇含海报/装饰线/信息区/内容卡片）

#### 2.3 渲染引擎 (`renderer.py`)
- [x] 根据 `category` 自动选择模板
- [x] 关键词蓝色加粗强调 `rgb(32,90,171)`
- [x] 图片路径解析（本地 `file:///` 绝对路径）
- [x] 讲座模板自动填充默认署名（美编/责编）
- [x] CLI 入口：`python -m tool2_layout.main <json> [--head-img] [--tail-img] [--no-preview]`

### 验收标准 ✅
- "a talk" 讲座文档完整渲染，浏览器预览效果与秀米排版一致
- 蓝色卡片、图片阴影、条纹装饰、头尾图 GIF、署名区均正确
- 所有 CSS 内联，微信兼容

---

## Phase 3：工具3 - 公众号草稿推送

### 目标
将排版好的 HTML → 通过微信公众号API上传为草稿 → 等待人工审核

### 任务拆解

#### 3.1 微信公众号 API 对接 (`wechat_api.py`)
- [ ] 研究微信公众号官方API文档：
  - 获取 access_token：`GET /cgi-bin/token`
  - 上传图片素材：`POST /cgi-bin/media/uploadimg`（文章内图片）
  - 上传永久素材：`POST /cgi-bin/material/add_material`（封面图）
  - 创建草稿：`POST /cgi-bin/draft/add`
- [ ] 封装 API 调用类，处理 token 刷新和错误重试
- [ ] 配置文件管理 AppID / AppSecret（config.json，加入 .gitignore）

#### 3.2 素材上传与HTML处理
- [ ] 上传文章内所有图片到微信服务器，获取微信图片URL
- [ ] 替换 HTML 中的本地图片路径为微信URL
- [ ] 上传封面图（从正文图片中选取，或使用默认封面）

#### 3.3 创建草稿
- [ ] 调用草稿接口，填入标题、摘要、正文HTML、封面
- [ ] 返回草稿链接/ID，方便后续在公众号后台查看
- [ ] 打印操作结果，提示用户登录后台审核

### 验收标准
- 运行脚本后，公众号后台出现新草稿
- 草稿内容、排版、图片均正确
- 不会自动发布，必须人工确认

---

## Phase 4：全流程串联

### 任务拆解
- [ ] 实现 `pipeline.py` 一键脚本，串联工具1→2→3
- [ ] 添加命令行参数：输入文件路径、模板选择、是否推送等
- [ ] 添加中间结果缓存（避免重复调用 LLM）
- [ ] 错误处理与日志输出

### 验收标准
- `python pipeline.py input.docx` 一条命令完成全流程
- 每步有清晰的终端输出，告知进度
- 出错时有明确提示，不会静默失败

---

## 未来扩展（暂不实施）

- [ ] Streamlit Web 界面（分享给其他同学使用时）
- [ ] 模板可视化编辑器（拖拽调整模板）
- [ ] 批量处理多篇稿件
- [ ] 历史推文数据库与搜索
- [ ] 自动选择最佳封面图（图片质量评估）
