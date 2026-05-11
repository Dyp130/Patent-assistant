import asyncio
from src.services.ai_service import chat, extract_json
from src.services.prompt_loader import load_prompt
from src.models.schemas import ConceptAnalysis


def analyze_concept(technical_concept: str) -> ConceptAnalysis:
    """Analyze a technical concept to extract structured features for patent drafting."""
    prompts = load_prompt("concept_analysis")
    user_message = prompts["user"].format(technical_concept=technical_concept)

    response = chat(
        system_prompt=prompts["system"],
        user_message=user_message,
        temperature=0.2,
        max_tokens=8000,
    )

    data = extract_json(response)
    return ConceptAnalysis(**data)


async def analyze_concept_async(technical_concept: str) -> ConceptAnalysis:
    """Async version of concept analysis."""
    return await asyncio.to_thread(analyze_concept, technical_concept)
