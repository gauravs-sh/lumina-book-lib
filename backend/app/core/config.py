from __future__ import annotations

from typing import List

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Smart QA Platform"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"

    database_url: AnyUrl = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/smart_qa",
        alias="DATABASE_URL",
    )

    jwt_secret: str = Field(default="CHANGE_ME", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="meta-llama/llama-3-8b-instruct", alias="OPENROUTER_MODEL")

    cors_origins: List[str] = Field(default=["http://localhost:5173"], alias="CORS_ORIGINS")

    admin_email: str = Field(default="admin@example.com", alias="ADMIN_EMAIL")
    admin_password: str = Field(default="Admin123!", alias="ADMIN_PASSWORD")

    storage_path: str = Field(default="./storage", alias="STORAGE_PATH")


settings = Settings()
