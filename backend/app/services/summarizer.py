from __future__ import annotations

from app.services.llm import LLMProvider


async def generate_summary(text: str, llm: LLMProvider) -> str:
    if not text.strip():
        return ""
    return await llm.summarize(text)
