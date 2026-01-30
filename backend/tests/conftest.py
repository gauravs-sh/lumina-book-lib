import importlib
import os
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.com")
os.environ.setdefault("ADMIN_PASSWORD", "Admin123!")

import app.core.config  # noqa: E402
import app.db.session  # noqa: E402

importlib.reload(app.core.config)
importlib.reload(app.db.session)

from app.main import app, init_models  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    db_path = Path("./test.db")
    if db_path.exists():
        db_path.unlink()
    await init_models()
    yield


@pytest.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
