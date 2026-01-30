from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.book import Book
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewRead

router = APIRouter(prefix="/books", tags=["reviews"])


@router.post("/{book_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def add_review(
    book_id: int,
    payload: ReviewCreate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Review:
    result = await session.execute(select(Book).where(Book.id == book_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    review = Review(book_id=book_id, user_id=user.id, review_text=payload.review_text, rating=payload.rating)
    session.add(review)
    await session.commit()
    await session.refresh(review)
    return review
