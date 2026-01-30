from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.document_chunk import DocumentChunk
from app.schemas.qa import AnswerResponse, QuestionRequest
from app.services.rag import select_relevant_chunks

router = APIRouter(prefix="/qa", tags=["qa"])
logger = logging.getLogger("smart_qa.qa")


async def _generate_answer(question: str, context: str) -> str:
    if not settings.openrouter_api_key:
        return f"Based on the provided documents: {context[:400]}"

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": "You answer questions using provided context only."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


@router.post("", response_model=AnswerResponse)
async def ask_question(
    payload: QuestionRequest,
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> AnswerResponse:
    result = await session.execute(select(DocumentChunk))
    chunks = list(result.scalars().all())
    if not chunks:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No ingested documents available")

    selected = select_relevant_chunks(payload.question, chunks)
    context = "\n\n".join(chunk.content for chunk in selected)
    answer = await _generate_answer(payload.question, context)
    return AnswerResponse(answer=answer, excerpts=[chunk.content for chunk in selected])
