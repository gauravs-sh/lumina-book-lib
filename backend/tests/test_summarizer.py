import pytest

from app.services.summarizer import generate_summary


@pytest.mark.asyncio
async def test_generate_summary_fallback():
    text = "Lorem ipsum " * 100
    summary = await generate_summary(text)
    assert summary
    assert len(summary) <= 500
