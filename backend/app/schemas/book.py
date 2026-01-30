from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    year_published: int = Field(ge=0, le=3000)
    content: str | None = None


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    year_published: int | None = Field(default=None, ge=0, le=3000)


class BookRead(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    year_published: int
    summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookSummaryRead(BaseModel):
    book_id: int
    summary: str | None
    average_rating: float
    total_reviews: int
