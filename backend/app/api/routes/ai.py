from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.qa import SummaryRequest
from app.services.summarizer import generate_summary

router = APIRouter(tags=["ai"])


@router.post("/generate-summary")
async def generate_summary_endpoint(payload: SummaryRequest, _: str = Depends(get_current_user)) -> dict[str, str]:
    summary = await generate_summary(payload.content)
    return {"summary": summary}
