# Patent Drafting Assistant (专利撰写助手)

AI-powered Chinese patent disclosure drafting tool. Input your core technical concept and let AI generate a complete 10-chapter patent disclosure document with streaming generation, per-chapter editing, figure prompts, version history, and DOCX/Markdown export.

## Features

- **AI-driven patent drafting**: Generate a complete patent disclosure from your core technical concept
- **10-chapter standard structure**: Title → Technical Field → Background Art → Purpose → Technical Solution → Beneficial Effects → Drawing Description → Detailed Embodiments → Alternative Embodiments → Key Points & Protection Scope
- **Concept-first workflow**: Describe your technical concept first, then generate chapters based on structured analysis
- **Technical feature analysis**: AI extracts key components, relationships, innovation points, and expected effects
- **Per-chapter generation & editing**: Single-chapter streaming generation, real-time preview, manual editing, Markdown preview
- **Figure prompts**: AI auto-inserts `[Figure N: description]` markers; right panel aggregates all figure requirements
- **Version history**: Auto-saved version snapshots on each edit, with rollback support
- **DOCX export**: Properly configured Chinese fonts (Song Ti / Hei Ti), compatible with Microsoft Word and WPS Office
- **Markdown export**: Easy import into other editing tools

## Quick Start

### Requirements

- Python 3.10+
- Access to an LLM API (Anthropic-compatible interface)

### Installation

```bash
git clone https://github.com/Dyp130/Patent-assistant.git
cd Patent-assistant

pip install -r requirements.txt
```

### Configure API

The project reads LLM API configuration through two methods (higher priority first):

**Option 1: Environment variables**

```bash
export ANTHROPIC_BASE_URL="https://api.deepseek.com"
export ANTHROPIC_AUTH_TOKEN="your-api-key"
export ANTHROPIC_MODEL="deepseek-chat"
```

**Option 2: Claude Code settings**

If you have Claude Code installed, the project auto-reads API config from `~/.claude/settings.json`.

### Launch

```bash
python run.py
```

Open **http://127.0.0.1:8000** in your browser.

## Usage Guide

### 1. Create a new project

Click "New Patent Draft" on the home page, select patent type (Invention / Utility Model / Design Patent), and enter your core technical concept.

### 2. Enter your technical concept

Describe your invention in detail:

- The technical problem to be solved
- Key components/elements and how they work together
- Differences from existing technology
- Expected technical effects

Click "Save Concept", and optionally "Analyze Technical Features" for AI-structured extraction.

### 3. Generate the patent disclosure

- **Generate All**: Click "Generate All" in the sidebar — AI generates chapters sequentially
- **Single Chapter**: Select a chapter and click "AI Generate"

Generation uses SSE streaming for real-time preview.

### 4. Edit & Review

- Edit AI-generated content in the editor
- Click "Preview" for Markdown-rendered view
- Each save creates a history version; rollback anytime

### 5. Manage figures

The right-side Figure Checklist panel auto-aggregates all `[Figure N: description]` markers from generated content.

### 6. Export

- **DOCX**: Export as Word document with proper Chinese formatting
- **Markdown**: Export as plain text markup file

## Patent Chapter Structure

| # | Chapter | Description |
|---|---------|-------------|
| 1 | Title | Concise and accurate, ≤25 characters |
| 2 | Technical Field | Specific technical domain of the invention |
| 3 | Background Art | 2-3 existing solutions and their shortcomings |
| 4 | Purpose | Technical problems to be solved |
| 5 | **Technical Solution** | Core chapter: components, relationships, parameters, mechanisms |
| 6 | Beneficial Effects | Quantitative/qualitative advantages over prior art |
| 7 | Drawing Description | Numbered list of all required figures with descriptions |
| 8 | Detailed Embodiments | At least one complete, reproducible embodiment |
| 9 | Alternative Embodiments | Optional variants and alternative implementations |
| 10 | Key Points & Protection | Innovation points ranked by importance, claim-ready |

## Project Structure

```
Patent-assistant/
├── config/
│   ├── settings.py           # Configuration (API keys, etc.)
│   ├── prompts.yaml          # AI prompt templates (customizable)
│   └── chapter_schema.yaml   # Chapter definitions
├── src/
│   ├── main.py               # FastAPI application entry
│   ├── routes/               # API routes
│   ├── models/               # Data models (SQLAlchemy)
│   ├── services/             # AI generation, export, analysis
│   ├── templates/            # Jinja2 frontend pages
│   └── static/               # CSS / JavaScript
├── data/                     # SQLite database (auto-created)
├── output/                   # Exported DOCX/MD files
├── requirements.txt
├── run.py                    # Launch script
└── README.md
```

## Customizing Prompts

AI generation quality depends on prompt quality. Edit `config/prompts.yaml` to adjust each chapter's generation strategy without modifying code. Prompts use `{variable}` placeholders for context injection.

## Tech Stack

- **Backend**: Python 3.10+ / FastAPI / SQLAlchemy / SQLite
- **Frontend**: Jinja2 templates + vanilla JavaScript + SSE streaming
- **AI**: Anthropic SDK (compatible with OpenAI / DeepSeek / etc.)
- **Export**: python-docx (with Chinese font configuration)

## License

MIT License — see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome. Please open an issue or pull request on GitHub.
