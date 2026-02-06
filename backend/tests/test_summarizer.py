import pytest

from app.services.summarizer import generate_summary
from app.api.deps import get_llm

@pytest.mark.asyncio
async def test_generate_summary_fallback():
    text = "Lorem ipsum " * 100
    llm = await get_llm()
    summary = await generate_summary(text, llm)
    assert summary
    assert len(summary) <= 500
