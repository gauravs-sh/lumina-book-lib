from __future__ import annotations

from typing import Protocol

import httpx

from app.core.config import settings


class LLMProvider(Protocol):
    async def summarize(self, content: str) -> str: ...

    async def analyze_reviews(self, content: str) -> str: ...


class MockLLM:
    async def summarize(self, content: str) -> str:
        snippet = content.strip().replace("\n", " ")[:240]
        return f"Summary (mock): {snippet}"

    async def analyze_reviews(self, content: str) -> str:
        snippet = content.strip().replace("\n", " ")[:240]
        return f"Consensus (mock): {snippet}"


class OpenRouterLLM:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def summarize(self, content: str) -> str:
        return await _openrouter_call(
            self.api_key,
            self.model,
            system_prompt="You summarize a book in 5 concise bullet points.",
            user_prompt=f"Book content:\n{content}\n\nProvide summary:",
        )

    async def analyze_reviews(self, content: str) -> str:
        return await _openrouter_call(
            self.api_key,
            self.model,
            system_prompt="You produce a rolling consensus of reader sentiment in 3 bullet points.",
            user_prompt=f"Reviews:\n{content}\n\nProvide consensus:",
        )


class HttpLLM:
    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def summarize(self, content: str) -> str:
        return await _openai_compatible_call(
            self.base_url,
            self.api_key,
            system_prompt="You summarize a book in 5 concise bullet points.",
            user_prompt=f"Book content:\n{content}\n\nProvide summary:",
        )

    async def analyze_reviews(self, content: str) -> str:
        return await _openai_compatible_call(
            self.base_url,
            self.api_key,
            system_prompt="You produce a rolling consensus of reader sentiment in 3 bullet points.",
            user_prompt=f"Reviews:\n{content}\n\nProvide consensus:",
        )


async def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
        return OpenRouterLLM(settings.openrouter_api_key, settings.openrouter_model)
    if settings.llm_provider == "http" and settings.llm_base_url:
        return HttpLLM(settings.llm_base_url, settings.llm_api_key)
    return MockLLM()


async def _openrouter_call(api_key: str, model: str, system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


async def _openai_compatible_call(base_url: str, api_key: str | None, system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": "local-llm",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{base_url}/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
