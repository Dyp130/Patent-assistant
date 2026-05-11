import json
import re
from collections.abc import AsyncGenerator, Generator
from anthropic import Anthropic, AsyncAnthropic
from config.settings import get_settings

settings = get_settings()


def _get_client() -> Anthropic:
    return Anthropic(
        base_url=settings.anthropic_base_url or None,
        api_key=settings.anthropic_api_key,
    )


def _get_async_client() -> AsyncAnthropic:
    return AsyncAnthropic(
        base_url=settings.anthropic_base_url or None,
        api_key=settings.anthropic_api_key,
    )


def chat(system_prompt: str, user_message: str, temperature: float = 0.3, max_tokens: int = 16000) -> str:
    """Synchronous chat completion."""
    client = _get_client()
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    # Extract text from first content block
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


async def chat_stream(
    system_prompt: str, user_message: str, temperature: float = 0.3, max_tokens: int = 16000
) -> AsyncGenerator[str, None]:
    """Async streaming chat completion."""
    client = _get_async_client()
    async with client.messages.stream(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


def extract_json(text: str) -> dict:
    """Extract JSON object from AI response that may contain extra text."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in markdown code fences
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try to find outermost braces
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    return {}
