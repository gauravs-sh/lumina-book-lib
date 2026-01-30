from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    review_text: str = Field(min_length=5)
    rating: int = Field(ge=1, le=5)


class ReviewRead(BaseModel):
    id: int
    book_id: int
    user_id: int
    review_text: str
    rating: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
