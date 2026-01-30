from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IngestionJobRead(BaseModel):
    id: int
    document_id: int
    status: str
    error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
