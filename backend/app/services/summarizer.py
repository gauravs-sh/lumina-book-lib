from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("smart_qa.summarizer")


async def generate_summary(text: str) -> str:
    if not text.strip():
        return ""

    if not settings.openrouter_api_key:
        logger.warning("OpenRouter API key not configured. Returning truncated summary.")
        return text[:500]

    prompt = (
        "Summarize the following content in 4-6 sentences. Keep it concise and factual.\n\n"
        f"{text}"
    )

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": "You are a helpful summarization assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 350,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
