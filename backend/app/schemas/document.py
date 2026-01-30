from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    filename: str
    content: str


class DocumentRead(BaseModel):
    id: int
    filename: str
    content: str
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
