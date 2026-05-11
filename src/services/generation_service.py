import re
import json
from typing import Optional
from collections.abc import AsyncGenerator

from sqlalchemy.orm import Session

from src.services.ai_service import chat, chat_stream, extract_json
from src.services.prompt_loader import load_prompt, get_chapter_config
from src.services.analysis_service import analyze_concept
from src.models.schemas import ConceptAnalysis


CHAPTER_KEY_MAP = {
    1: "chapter_1_title",
    2: "chapter_2_technical_field",
    3: "chapter_3_background_art",
    4: "chapter_4_purpose",
    5: "chapter_5_technical_solution",
    6: "chapter_6_beneficial_effects",
    7: "chapter_7_drawing_description",
    8: "chapter_8_detailed_embodiments",
    9: "chapter_9_alternative_embodiments",
    10: "chapter_10_key_points",
}

CHAPTER_CONTENT_KEY = {
    1: "title",
    2: "technical_field",
    3: "background_art",
    4: "purpose",
    5: "technical_solution",
    6: "beneficial_effects",
    7: "drawing_description",
    8: "detailed_embodiments",
    9: "alternative_embodiments",
    10: "key_points",
}


def extract_figure_placeholders(content: str) -> list[dict]:
    """Parse [插入图N: 描述] markers from content."""
    pattern = r"\[插入图(\d+)[：:]\s*([^\]]+)\]"
    results = []
    for m in re.finditer(pattern, content):
        results.append({
            "position_label": f"图{m.group(1)}",
            "description": m.group(2).strip(),
            "position_marker": m.start(),
        })
    return results


def _build_context(concept: str, analysis: ConceptAnalysis, previous: dict) -> dict:
    """Build template variables for a chapter prompt."""
    ctx = {
        "technical_concept": concept,
        "concept_analysis": json.dumps(analysis.model_dump(), ensure_ascii=False, indent=2),
    }
    # Inject all previously generated chapter content
    chapter_keys = list(CHAPTER_CONTENT_KEY.values())
    for key in chapter_keys:
        ctx[key] = previous.get(key, "(待生成)")
    return ctx


def generate_chapter_sync(
    chapter_order: int,
    technical_concept: str,
    analysis: ConceptAnalysis,
    previous_chapters: dict,
) -> str:
    """Synchronously generate a single chapter."""
    prompt_key = CHAPTER_KEY_MAP.get(chapter_order)
    if not prompt_key:
        return ""

    prompts = load_prompt(prompt_key)
    ctx = _build_context(technical_concept, analysis, previous_chapters)
    user_message = prompts["user"].format(**ctx)

    return chat(
        system_prompt=prompts["system"],
        user_message=user_message,
        temperature=0.3,
        max_tokens=16000,
    )


async def generate_chapter_stream(
    chapter_order: int,
    technical_concept: str,
    analysis: ConceptAnalysis,
    previous_chapters: dict,
) -> AsyncGenerator[str, None]:
    """Async streaming generation of a single chapter."""
    prompt_key = CHAPTER_KEY_MAP.get(chapter_order)
    if not prompt_key:
        return

    prompts = load_prompt(prompt_key)
    ctx = _build_context(technical_concept, analysis, previous_chapters)
    user_message = prompts["user"].format(**ctx)

    async for token in chat_stream(
        system_prompt=prompts["system"],
        user_message=user_message,
        temperature=0.3,
        max_tokens=16000,
    ):
        yield token


def generate_all_chapters_sync(
    technical_concept: str,
    patent_type: str = "发明专利",
) -> list[dict]:
    """Synchronously generate all chapters. Returns list of {order, key, name, content}."""
    analysis = analyze_concept(technical_concept)
    chapter_configs = get_chapter_config()
    previous: dict = {}

    results = []
    for cfg in sorted(chapter_configs, key=lambda c: c["order"]):
        order = cfg["order"]
        content = generate_chapter_sync(order, technical_concept, analysis, previous)
        key = CHAPTER_CONTENT_KEY.get(order, cfg["key"])
        previous[key] = content
        figures = extract_figure_placeholders(content)
        results.append({
            "order": order,
            "key": cfg["key"],
            "name": cfg["name"],
            "content": content,
            "figures": figures,
        })

    return results
