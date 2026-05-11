import json
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "专利撰写助手"
    app_version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000

    # Database
    db_path: str = str(Path(__file__).parent.parent / "data" / "patent_assistant.db")

    # AI / LLM — read from existing Claude settings or env vars
    anthropic_base_url: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "DeepSeek-V4-pro[1m]"

    # Output directory
    output_dir: str = str(Path(__file__).parent.parent / "output")

    model_config = {"env_prefix": "PATENT_", "env_file": ".env", "extra": "ignore"}


def _load_from_claude_settings() -> dict:
    """Try to read API credentials from the existing Claude Code settings."""
    claude_settings = Path.home() / ".claude" / "settings.json"
    result = {}
    if claude_settings.exists():
        try:
            data = json.loads(claude_settings.read_text(encoding="utf-8"))
            env = data.get("env", {})
            if env.get("ANTHROPIC_BASE_URL"):
                result["anthropic_base_url"] = env["ANTHROPIC_BASE_URL"]
            if env.get("ANTHROPIC_AUTH_TOKEN"):
                result["anthropic_api_key"] = env["ANTHROPIC_AUTH_TOKEN"]
            if env.get("ANTHROPIC_MODEL"):
                result["anthropic_model"] = env["ANTHROPIC_MODEL"]
        except (json.JSONDecodeError, OSError):
            pass
    return result


def get_settings() -> Settings:
    claude_overrides = _load_from_claude_settings()
    s = Settings()
    for key, value in claude_overrides.items():
        if value:
            setattr(s, key, value)
    return s
