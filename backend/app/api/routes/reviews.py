from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_llm
from app.models.borrow import BookBorrow
from app.models.book import Book
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewRead
from app.db.session import SessionLocal
from app.services.review_analysis import generate_review_summary

router = APIRouter(prefix="/books", tags=["reviews"])


async def _update_review_summary(book_id: int) -> None:
    llm = await get_llm()
    async with SessionLocal() as session:
        review_result = await session.execute(select(Review).where(Review.book_id == book_id))
        reviews = list(review_result.scalars().all())
        summary = await generate_review_summary([review.review_text for review in reviews], llm)
        book_result = await session.execute(select(Book).where(Book.id == book_id))
        book = book_result.scalar_one_or_none()
        if book:
            book.review_summary = summary
            await session.commit()


@router.post("/{book_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def add_review(
    book_id: int,
    payload: ReviewCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Review:
    result = await session.execute(select(Book).where(Book.id == book_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    borrow_result = await session.execute(
        select(BookBorrow).where(
            BookBorrow.book_id == book_id,
            BookBorrow.user_id == user.id,
        )
    )
    if not borrow_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Borrow the book before reviewing")

    review = Review(book_id=book_id, user_id=user.id, review_text=payload.review_text, rating=payload.rating)
    session.add(review)
    await session.commit()
    await session.refresh(review)
    background_tasks.add_task(_update_review_summary, book_id)
    return review
