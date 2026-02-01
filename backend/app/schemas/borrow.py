from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BorrowRead(BaseModel):
    id: int
    book_id: int
    user_id: int
    borrowed_at: datetime
    returned_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class BorrowStatusRead(BaseModel):
    status: str
    borrowed_at: datetime | None = None
    returned_at: datetime | None = None
