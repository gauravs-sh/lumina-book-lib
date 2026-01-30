from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.book import Book
from app.models.review import Review
from app.schemas.book import BookCreate, BookRead, BookSummaryRead, BookUpdate
from app.schemas.review import ReviewRead
from app.db.session import SessionLocal
from app.services.summarizer import generate_summary

router = APIRouter(prefix="/books", tags=["books"])


async def _update_book_summary(book_id: int, content: str) -> None:
    summary = await generate_summary(content)
    async with SessionLocal() as session:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        if book:
            book.summary = summary
            await session.commit()


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Book:
    book = Book(
        title=payload.title,
        author=payload.author,
        genre=payload.genre,
        year_published=payload.year_published,
    )
    session.add(book)
    await session.commit()
    await session.refresh(book)

    if payload.content:
        background_tasks.add_task(_update_book_summary, book.id, payload.content)

    return book


@router.get("", response_model=list[BookRead])
async def list_books(session: AsyncSession = Depends(get_db)) -> list[Book]:
    result = await session.execute(select(Book))
    return list(result.scalars().all())


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, session: AsyncSession = Depends(get_db)) -> Book:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Book:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)

    await session.commit()
    await session.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await session.delete(book)
    await session.commit()


@router.get("/{book_id}/reviews", response_model=list[ReviewRead])
async def list_reviews(book_id: int, session: AsyncSession = Depends(get_db)) -> list[Review]:
    result = await session.execute(select(Review).where(Review.book_id == book_id))
    return list(result.scalars().all())


@router.get("/{book_id}/summary", response_model=BookSummaryRead)
async def get_book_summary(book_id: int, session: AsyncSession = Depends(get_db)) -> BookSummaryRead:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    review_result = await session.execute(select(Review).where(Review.book_id == book_id))
    reviews = list(review_result.scalars().all())
    average_rating = sum(review.rating for review in reviews) / len(reviews) if reviews else 0.0

    return BookSummaryRead(
        book_id=book.id,
        summary=book.summary,
        average_rating=round(average_rating, 2),
        total_reviews=len(reviews),
    )
