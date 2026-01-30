from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentRead

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Document:
    document = Document(filename=payload.filename, content=payload.content, owner_id=user.id)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Document:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")
    content = (await file.read()).decode("utf-8", errors="ignore")
    document = Document(filename=file.filename, content=content, owner_id=user.id)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Document]:
    result = await session.execute(select(Document).where(Document.owner_id == user.id))
    return list(result.scalars().all())


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Document:
    result = await session.execute(
        select(Document).where(Document.id == document_id, Document.owner_id == user.id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
