# Contributing to Patent Drafting Assistant

Thanks for your interest in contributing.

## How to Contribute

### Reporting Bugs

Open an issue with:
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error logs if applicable

### Feature Requests

Open an issue describing:
- What problem the feature solves
- How it should work
- Any alternatives considered

### Pull Requests

1. Fork the repo and create a branch from `master`
2. Make your changes
3. Ensure the project runs (`python run.py`)
4. Open a PR with a clear description

### Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/Patent-assistant.git
cd Patent-assistant
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API credentials
python run.py
```

## Style Guide

- Python: Follow PEP 8
- Frontend: Keep vanilla JS/CSS, no build tools required
- Prompts: Edit `config/prompts.yaml` for AI behavior changes
