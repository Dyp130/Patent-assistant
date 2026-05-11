import yaml
from pathlib import Path

_PROMPTS_CACHE = None


def _load_prompts() -> dict:
    global _PROMPTS_CACHE
    if _PROMPTS_CACHE is None:
        path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
        with open(path, encoding="utf-8") as f:
            _PROMPTS_CACHE = yaml.safe_load(f)
    return _PROMPTS_CACHE


def load_prompt(prompt_key: str) -> dict:
    """Load a specific prompt's system and user templates."""
    prompts = _load_prompts()
    prompt = prompts.get(prompt_key, {})
    if isinstance(prompt, dict):
        return {"system": prompt.get("system", ""), "user": prompt.get("user", "")}
    return {"system": "", "user": ""}


def load_chapter_prompt(prompt_key: str) -> dict:
    """Load a chapter-specific prompt."""
    return load_prompt(prompt_key)


def get_chapter_config() -> list[dict]:
    """Load chapter configuration from chapter_schema.yaml."""
    path = Path(__file__).parent.parent.parent / "config" / "chapter_schema.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("chapters", [])
