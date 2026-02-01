from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UserPreferencesUpdate(BaseModel):
    preferences: dict


class UserPreferencesRead(BaseModel):
    id: int
    user_id: int
    preferences: dict

    model_config = ConfigDict(from_attributes=True)
