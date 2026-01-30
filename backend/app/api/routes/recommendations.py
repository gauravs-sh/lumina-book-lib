from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_admin
from app.models.book import Book
from app.schemas.book import BookRead
from app.services.recommender import recommend_books, recommend_similar_books
from app.services.recommender_model import recommend_from_model, train_recommender

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[BookRead])
async def get_recommendations(
    genres: str | None = None,
    book_id: int | None = None,
    limit: int = 5,
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[Book]:
    result = await session.execute(select(Book))
    books = list(result.scalars().all())
    if book_id:
        target = next((book for book in books if book.id == book_id), None)
        if target:
            model_results = recommend_from_model(target, books, limit=limit)
            if model_results:
                return model_results
            return recommend_similar_books(target, books, limit=limit)

    preferred_genres = [genre.strip() for genre in genres.split(",")] if genres else []
    return recommend_books(books, preferred_genres=preferred_genres, limit=limit)


@router.post("/train")
async def train_recommendation_model(
    session: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin),
) -> dict[str, str]:
    result = await session.execute(select(Book))
    books = list(result.scalars().all())
    return train_recommender(books)
