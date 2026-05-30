<h1 align="center">专利撰写助手</h1>
<p align="center"><strong>Patent Drafting Assistant — AI 驱动的专利交底书撰写工具</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/AI-Anthropic%20SDK-8b5cf6" alt="Anthropic SDK">
  <a href="https://pypi.org/project/patent-drafting-assistant/"><img src="https://img.shields.io/pypi/v/patent-drafting-assistant?color=3775A9&logo=pypi&logoColor=white" alt="PyPI"></a>
  <a href="https://pypi.org/project/patent-drafting-assistant/"><img src="https://img.shields.io/pypi/dm/patent-drafting-assistant?color=3775A9" alt="Downloads"></a>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用指南">使用指南</a> •
  <a href="#章节结构">章节结构</a> •
  <a href="#自定义提示词">自定义提示词</a> •
  <a href="#参与贡献">参与贡献</a>
</p>

---

输入核心技术构思，AI 自动生成符合中国专利法规范的 10 章节完整交底书。支持流式生成、逐章编辑、自动附图提示、版本回退、DOCX/Markdown 导出，全部通过清爽的本地 Web 界面操作。

## 功能特性

- **AI 自动撰写** — 输入核心技术构思，AI 逐章生成完整专利交底书
- **10 章节标准结构** — 符合中国专利交底书规范
- **构思优先工作流** — 先输入技术构思，AI 分析后再基于结果逐章生成
- **技术特征分析** — AI 自动提取关键要素、创新点、预期效果
- **流式生成** — SSE 实时输出，随时查看生成进度
- **逐章编辑** — 支持手动编辑、Markdown 实时预览切换
- **附图提示** — AI 自动标记 `[图N: 描述]`，右侧面板汇总附图清单
- **版本回退** — 每次保存自动快照，一键恢复任意历史版本
- **DOCX 导出** — 正确配置宋体/黑体中文字体，兼容 Word 和 WPS
- **Markdown 导出** — 便于导入其他编辑工具
- **零配置启动** — 自动读取 Claude Code 配置或环境变量中的 API Key

## 快速开始

### 环境要求

- Python **3.10+**
- 可访问的 LLM API（兼容 Anthropic SDK，如 DeepSeek / OpenAI / Claude）

### 安装

```bash
# 方式一：pip 安装
pip install patent-drafting-assistant
patent-assistant

# 方式二：源码运行
git clone https://github.com/Dyp130/Patent-assistant.git
cd Patent-assistant
pip install -r requirements.txt
python run.py
```

### 配置 API

复制示例配置文件并填入凭据：

```bash
cp .env.example .env
# 编辑 .env：填写 API 地址、密钥、模型名称
```

或者通过环境变量设置：

```bash
export ANTHROPIC_BASE_URL="https://api.deepseek.com"
export ANTHROPIC_AUTH_TOKEN="your-api-key"
export ANTHROPIC_MODEL="deepseek-chat"
```

如果已安装 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)，应用会自动读取 `~/.claude/settings.json` 中的 API 配置。

### 启动

```bash
python run.py
# 打开 http://127.0.0.1:8000
```

## 使用指南

### 操作流程

| 步骤 | 操作 |
|------|------|
| 1 | 点击「新建专利草稿」，选择专利类型，输入核心技术构思 |
| 2 | 点击「保存构思」，可选「分析技术特征」让 AI 提取结构化信息 |
| 3 | 点击「全部生成」一键生成所有章节，或选中单章点击「AI 生成」 |
| 4 | 逐章审核、编辑、预览 |
| 5 | 导出为 **DOCX** 或 **Markdown** |

### 界面截图

<!-- TODO: 添加截图 -->
<p align="center">
  <em>截图即将补充 — 运行 <code>python run.py</code> 即可体验。</em>
</p>

## 章节结构

| 序号 | 章节名称 | 说明 |
|------|----------|------|
| 1 | 发明名称 | 简洁准确，一般不超过 25 字，不使用营销性词汇 |
| 2 | 技术领域 | 发明所属的具体技术细分领域 |
| 3 | 背景技术 | 引证 2-3 项现有方案，指出其不足之处 |
| 4 | 发明目的 | 明确要解决的技术问题 |
| 5 | **技术方案** | 核心章节：要素构成、关系、机制、参数等 |
| 6 | 有益效果 | 与现有技术对比，定量或定性说明优势 |
| 7 | 附图说明 | 列出所有附图的编号和描述 |
| 8 | 具体实施方式 | 至少一个完整可重现的实施例 |
| 9 | 替代方案 | 可选的变体或替代实现方式 |
| 10 | 关键点与保护点 | 按重要性排列的创新要点 |

## 自定义提示词

编辑 `config/prompts.yaml` 即可调整每个章节的 AI 生成策略，无需修改代码。提示词使用 `{变量}` 占位符注入上下文。

```yaml
chapter_5_technical_solution:
  system: |
    你是一位资深的中国专利代理人。
    请根据以下核心技术构思，撰写"技术方案"章节。
    ...
  user: |
    发明名称：{title}
    核心技术构思：{technical_concept}
    ...
```

## 项目结构

```
Patent-assistant/
├── config/
│   ├── settings.py           # 配置读取（API 密钥等）
│   ├── prompts.yaml          # AI 提示词模板
│   └── chapter_schema.yaml   # 章节定义
├── src/
│   ├── main.py               # FastAPI 应用入口
│   ├── db/                   # 数据库（SQLAlchemy + SQLite）
│   ├── routes/               # API 路由
│   ├── models/               # ORM 模型和 Pydantic 校验
│   ├── services/             # AI 生成、分析、导出服务
│   ├── templates/            # Jinja2 前端页面
│   └── static/               # CSS 和原生 JavaScript
├── .env.example              # API 配置模板
├── requirements.txt
├── run.py                    # 启动脚本
└── README.md
```

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy |
| 数据库 | SQLite（零配置，自动创建） |
| 前端 | Jinja2 + 原生 JavaScript + SSE 流式传输 |
| AI | Anthropic SDK（兼容 DeepSeek / OpenAI / Claude） |
| 导出 | python-docx（中文字体配置）、Markdown |
| 设计 | 无前端构建工具，单文件 CSS |

## 参与贡献

欢迎参与贡献 — 详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

1. Fork 本项目
2. 创建分支（`git checkout -b feat/新功能`）
3. 提交更改
4. 推送并创建 Pull Request

## 许可证

MIT — 详见 [LICENSE](LICENSE)。
