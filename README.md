# 专利撰写助手 (Patent Drafting Assistant)

基于 AI 的中国专利交底书自动撰写工具，专注于**结构设计**领域。输入核心技术构思，自动生成符合中国专利法要求的 10 章节交底书，支持逐章编辑、附图提示、版本管理和 DOCX 导出。

## 功能特性

- **AI 驱动的专利撰写**：基于核心技术构思，自动生成完整的专利交底书
- **10 章节标准结构**：发明名称 → 技术领域 → 背景技术 → 发明目的 → 技术方案 → 有益效果 → 附图说明 → 具体实施方式 → 替代方案 → 关键点与保护点
- **构思优先工作流**：先输入并分析核心技术构思，再基于分析结果逐章生成
- **技术特征分析**：AI 自动提取关键构件、连接方式、创新点、预期效果等
- **逐章生成与编辑**：支持单章生成、流式实时预览、手动编辑、Markdown 预览
- **附图智能提示**：AI 在文档中自动标记 `[插入图N: 描述]`，右侧面板汇总所有附图清单
- **版本历史**：每次编辑自动保存历史版本，支持回退
- **DOCX 导出**：正确配置中文字体（宋体/黑体），兼容 Microsoft Word 和 WPS Office
- **Markdown 导出**：便于导入其他编辑工具

## 快速开始

### 环境要求

- Python 3.10+
- 可访问的 LLM API（支持 Anthropic 兼容接口）

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/Dyp130/Patent-assistant.git
cd Patent-assistant

# 2. 安装依赖
pip install -r requirements.txt
```

### 配置 API

项目通过以下两种方式读取 LLM API 配置（优先级从高到低）：

**方式一：环境变量**

```bash
export ANTHROPIC_BASE_URL="https://api.deepseek.com"   # API 地址
export ANTHROPIC_AUTH_TOKEN="your-api-key"             # API 密钥
export ANTHROPIC_MODEL="deepseek-chat"                 # 模型名称（可选）
```

**方式二：Claude Code 配置文件**

如果你已安装 Claude Code，项目会自动读取 `~/.claude/settings.json` 中的 API 配置，无需额外设置。

### 启动

```bash
python run.py
```

启动后访问 **http://127.0.0.1:8000**

## 使用指南

### 1. 创建新项目

在首页点击「新建专利草稿」，选择专利类型（发明专利/实用新型/外观设计），输入核心技术构思描述。

### 2. 输入核心技术构思

进入项目页后，在「关键核心技术构思」区域详细描述您的发明：

- 要解决的技术问题
- 关键构件的结构和连接关系
- 与现有技术的区别
- 预期的技术效果

点击「保存构思」，可选「分析技术特征」让 AI 提取结构化信息。

### 3. 生成专利交底书

- **全部生成**：左侧边栏点击「⚡ 全部生成」，AI 将按章节顺序逐一生成
- **单章生成**：点击左侧章节列表中的章节，在编辑器中点击「🤖 AI生成」

生成过程支持 SSE 流式输出，可实时查看生成进度。

### 4. 编辑与审核

- 在编辑器中对 AI 生成内容进行修改
- 点击「预览」查看 Markdown 渲染效果
- 每次保存自动创建历史版本，可随时回退

### 5. 管理附图

右侧「附图清单」面板自动汇总所有章节中的 `[插入图N: 描述]` 标记，帮助您准备对应的技术插图。

### 6. 导出文档

- **DOCX**：导出为 Word 文档，可直接用 Microsoft Word 或 WPS 打开编辑
- **Markdown**：导出为纯文本标记文件

## 专利章节结构

| 章节 | 名称 | 说明 |
|------|------|------|
| 1 | 发明名称 | 简洁准确，不超过 25 字 |
| 2 | 技术领域 | 发明所属的具体技术领域 |
| 3 | 背景技术 | 现有技术及其不足之处 |
| 4 | 发明目的 | 要解决的技术问题 |
| 5 | **技术方案** | 核心章节：构件、连接、材料、参数 |
| 6 | 有益效果 | 与现有技术对比的效果说明 |
| 7 | 附图说明 | 各附图的编号和简要描述 |
| 8 | 具体实施方式 | 完整可重现的实施例 |
| 9 | 替代方案 | 构件的变体或替代实现（可选） |
| 10 | 关键点与保护点 | 按重要性排列的创新要点 |

## 项目结构

```
Patent-assistant/
├── config/
│   ├── settings.py          # 配置读取（API 密钥等）
│   ├── prompts.yaml         # AI 提示词模板（可按需调整）
│   └── chapter_schema.yaml  # 章节定义
├── src/
│   ├── main.py              # FastAPI 应用入口
│   ├── routes/              # API 路由
│   ├── models/              # 数据模型
│   ├── services/            # AI 生成、导出等核心服务
│   ├── templates/           # Jinja2 前端页面
│   └── static/              # CSS / JavaScript
├── data/                    # SQLite 数据库（自动创建）
├── output/                  # 导出的 DOCX/MD 文件
├── requirements.txt
├── run.py                   # 启动脚本
└── README.md
```

## 自定义提示词

AI 生成质量取决于提示词质量。你可以编辑 `config/prompts.yaml` 来调整每个章节的生成策略，无需修改代码。提示词使用 `{variable}` 占位符注入上下文。

## 技术栈

- **后端**: Python 3.14 + FastAPI + SQLAlchemy + SQLite
- **前端**: Jinja2 模板 + 原生 JavaScript + SSE 流式传输
- **AI**: Anthropic SDK（兼容 OpenAI/DeepSeek 等接口）
- **导出**: python-docx（中文字体配置）

## 许可证

Private — 仅供个人使用。
