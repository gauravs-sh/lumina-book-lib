from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response
import json
from sqlalchemy import select

from app.api.routes import ai, auth, books, documents, ingestion, qa, recommendations, reviews, users
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import book, borrow, document, document_chunk, ingestion_job, review, user, user_preference
from app.models.user import User

configure_logging()
logger = logging.getLogger("smart_qa")


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == settings.admin_email))
        if not result.scalar_one_or_none():
            admin = User(
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                role="admin",
            )
            session.add(admin)
            await session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_models()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def response_wrapper(request: Request, call_next):
    if request.url.path in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
        return await call_next(request)
    response = await call_next(request)
    if response.status_code == 204:
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    content_type = response.headers.get("content-type", "")
    response_headers = dict(response.headers)
    response_headers.pop("content-length", None)
    if "application/json" not in content_type:
        return Response(
            content=body,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.media_type,
        )

    try:
        payload = json.loads(body.decode("utf-8")) if body else None
    except json.JSONDecodeError:
        return Response(
            content=body,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.media_type,
        )

    if isinstance(payload, dict) and {"status", "data", "error_message"}.issubset(payload.keys()):
        wrapped = payload
    else:
        error_message = None
        data = payload
        if response.status_code >= 400:
            error_message = None
            if isinstance(payload, dict):
                error_message = payload.get("error_message") or payload.get("detail")
            data = None
        wrapped = {"status": response.status_code, "data": data, "error_message": error_message}

    return JSONResponse(status_code=response.status_code, content=wrapped, headers=response_headers)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(ai.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(books.router, prefix=settings.api_v1_prefix)
app.include_router(reviews.router, prefix=settings.api_v1_prefix)
app.include_router(documents.router, prefix=settings.api_v1_prefix)
app.include_router(ingestion.router, prefix=settings.api_v1_prefix)
app.include_router(qa.router, prefix=settings.api_v1_prefix)
app.include_router(recommendations.router, prefix=settings.api_v1_prefix)


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error_message": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"error_message": "Internal server error"})


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
