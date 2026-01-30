from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.ingestion_job import IngestionJob
from app.models.user import User
from app.schemas.ingestion import IngestionJobRead
from app.services.ingestion import build_embeddings

router = APIRouter(prefix="/ingestion", tags=["ingestion"])
logger = logging.getLogger("smart_qa.ingestion")


async def _process_ingestion(job_id: int, document_id: int) -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(IngestionJob).where(IngestionJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            return

        job.status = "running"
        await session.commit()

        try:
            doc_result = await session.execute(select(Document).where(Document.id == document_id))
            document = doc_result.scalar_one_or_none()
            if not document:
                job.status = "failed"
                job.error = "Document not found"
                await session.commit()
                return

            embeddings = build_embeddings(document.content)
            for chunk, embedding in embeddings:
                session.add(DocumentChunk(document_id=document_id, content=chunk, embedding=embedding))

            job.status = "completed"
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Ingestion failed: %s", exc)
            job.status = "failed"
            job.error = str(exc)
            await session.commit()


@router.post("/{document_id}", response_model=IngestionJobRead, status_code=status.HTTP_202_ACCEPTED)
async def start_ingestion(
    document_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IngestionJob:
    result = await session.execute(
        select(Document).where(Document.id == document_id, Document.owner_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    job = IngestionJob(document_id=document_id, status="pending")
    session.add(job)
    await session.commit()
    await session.refresh(job)

    asyncio.create_task(_process_ingestion(job.id, document_id))
    return job


@router.get("/jobs", response_model=list[IngestionJobRead])
async def list_jobs(session: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> list[IngestionJob]:
    result = await session.execute(select(IngestionJob))
    return list(result.scalars().all())


@router.get("/jobs/{job_id}", response_model=IngestionJobRead)
async def get_job(job_id: int, session: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> IngestionJob:
    result = await session.execute(select(IngestionJob).where(IngestionJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
