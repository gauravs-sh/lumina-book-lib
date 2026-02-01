from __future__ import annotations

from app.services.llm import LLMProvider


def build_review_corpus(reviews: list[str]) -> str:
    return "\n".join(reviews)


async def generate_review_summary(reviews: list[str], llm: LLMProvider) -> str:
    if not reviews:
        return ""
    corpus = build_review_corpus(reviews)
    return await llm.analyze_reviews(corpus)
