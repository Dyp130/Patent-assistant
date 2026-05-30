<h1 align="center">Patent Drafting Assistant</h1>
<p align="center"><strong>专利撰写助手 — AI-powered patent disclosure drafting</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/AI-Anthropic%20SDK-8b5cf6" alt="Anthropic SDK">
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#usage">Usage</a> •
  <a href="#chapter-structure">Structure</a> •
  <a href="#customizing">Customize</a> •
  <a href="#contributing">Contributing</a>
</p>

---

Input your core technical concept and let AI generate a complete 10-chapter Chinese patent disclosure. Supports streaming generation, per-chapter editing, auto figure prompts, version history, and DOCX/Markdown export — all through a clean local web UI.

## Features

- **AI-driven drafting** — Generate a complete patent disclosure from a single technical concept
- **10-chapter standard structure** — Follows Chinese patent disclosure conventions
- **Concept-first workflow** — Analyze your concept first, then generate chapters based on structured extraction
- **Technical feature analysis** — AI extracts key elements, innovation points, and expected effects
- **Streaming generation** — Watch each chapter generate in real time via SSE
- **Per-chapter editing** — Edit any chapter manually, switch between Markdown edit and preview modes
- **Auto figure prompts** — AI inserts `[Figure N: description]` markers; right panel shows the figure checklist
- **Version history** — Every save creates a snapshot; rollback anytime
- **DOCX export** — Professional Word documents with correct Chinese fonts (Song Ti / Hei Ti)
- **Markdown export** — Plain text for other editing tools
- **Zero-config LLM** — Auto-reads API keys from Claude Code settings or environment variables

## Quick Start

### Prerequisites

- Python **3.10+**
- An Anthropic-compatible LLM API (e.g. DeepSeek, OpenAI, Claude)

### Install

```bash
git clone https://github.com/Dyp130/Patent-assistant.git
cd Patent-assistant
pip install -r requirements.txt
```

### Configure

Copy the example env file and set your credentials:

```bash
cp .env.example .env
# Edit .env with your API key, base URL, and model
```

Or export as environment variables:

```bash
export ANTHROPIC_BASE_URL="https://api.deepseek.com"
export ANTHROPIC_AUTH_TOKEN="your-api-key"
export ANTHROPIC_MODEL="deepseek-chat"
```

If you have [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed, the app automatically reads API config from `~/.claude/settings.json`.

### Launch

```bash
python run.py
```

Open **http://127.0.0.1:8000**

## Usage

### Workflow

| Step | Action |
|------|--------|
| 1 | Click **New Patent Draft**, choose patent type, and enter your core technical concept |
| 2 | Click **Save Concept**, then optionally **Analyze Technical Features** |
| 3 | Click **Generate All** (or select individual chapters via **AI Generate**) |
| 4 | Review, edit, and preview each chapter |
| 5 | Export as **DOCX** or **Markdown** |

### Screenshots

<!-- TODO: add screenshots -->
<p align="center">
  <em>Screenshots coming soon — run <code>python run.py</code> to see it in action.</em>
</p>

## Chapter Structure

| # | Chapter (EN) | Chapter (中文) | Description |
|---|-------------|---------------|-------------|
| 1 | Title | 发明名称 | Concise, ≤25 characters, no marketing terms |
| 2 | Technical Field | 技术领域 | Specific technical domain |
| 3 | Background Art | 背景技术 | 2-3 existing solutions and their shortcomings |
| 4 | Purpose | 发明目的 | Technical problems to be solved |
| 5 | **Technical Solution** | **技术方案** | Core chapter: elements, relationships, mechanisms |
| 6 | Beneficial Effects | 有益效果 | Quantitative/qualitative advantages |
| 7 | Drawing Description | 附图说明 | Numbered list of all required figures |
| 8 | Detailed Embodiments | 具体实施方式 | At least one complete, reproducible embodiment |
| 9 | Alternative Embodiments | 替代方案 | Optional variants and alternatives |
| 10 | Key Points & Protection | 关键点与保护点 | Innovation points ranked by importance |

## Customizing

Edit `config/prompts.yaml` to adjust AI generation behavior for each chapter — no code changes needed. Variables use `{placeholder}` syntax.

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

## Project Structure

```
Patent-assistant/
├── config/
│   ├── settings.py           # Configuration & env reading
│   ├── prompts.yaml          # AI prompt templates
│   └── chapter_schema.yaml   # Chapter definitions
├── src/
│   ├── main.py               # FastAPI application entry
│   ├── db/                   # Database setup (SQLAlchemy + SQLite)
│   ├── routes/               # Project, chapter, generation, export APIs
│   ├── models/               # ORM models and Pydantic schemas
│   ├── services/             # AI generation, analysis, export
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS & vanilla JavaScript
├── .env.example              # API configuration template
├── requirements.txt
├── run.py                    # Launch script
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+ / FastAPI / SQLAlchemy |
| Database | SQLite (zero-config, auto-created) |
| Frontend | Jinja2 + vanilla JS + SSE streaming |
| AI | Anthropic SDK (DeepSeek / OpenAI / Claude compatible) |
| Export | python-docx (Chinese font configured), markdown |
| Design | Zero build tools, single CSS file |

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repo
2. Create a branch (`git checkout -b feat/your-feature`)
3. Commit your changes
4. Push and open a Pull Request

## License

MIT — see [LICENSE](LICENSE).
