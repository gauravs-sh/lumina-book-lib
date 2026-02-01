from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from app.core.config import settings


class StorageProvider(Protocol):
    async def save(self, filename: str, content: bytes) -> str: ...

    async def read(self, key: str) -> bytes: ...

    async def delete(self, key: str) -> None: ...


class LocalStorage:
    def __init__(self, base_path: str) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, filename: str, content: bytes) -> str:
        ext = Path(filename).suffix
        key = f"{uuid4().hex}{ext}"
        path = self.base_path / key
        await _write_bytes(path, content)
        return key

    async def read(self, key: str) -> bytes:
        path = self.base_path / key
        return await _read_bytes(path)

    async def delete(self, key: str) -> None:
        path = self.base_path / key
        if path.exists():
            await _delete_file(path)


class S3Storage:
    def __init__(self, bucket: str, endpoint: str | None = None) -> None:
        import boto3

        self.bucket = bucket
        self.client = boto3.client("s3", endpoint_url=endpoint)

    async def save(self, filename: str, content: bytes) -> str:
        key = f"{uuid4().hex}-{os.path.basename(filename)}"
        await _run_blocking(self.client.put_object, Bucket=self.bucket, Key=key, Body=content)
        return key

    async def read(self, key: str) -> bytes:
        response = await _run_blocking(self.client.get_object, Bucket=self.bucket, Key=key)
        body = response["Body"].read()
        return body

    async def delete(self, key: str) -> None:
        await _run_blocking(self.client.delete_object, Bucket=self.bucket, Key=key)


async def get_storage_provider() -> StorageProvider:
    if settings.storage_provider == "s3":
        if not settings.storage_bucket:
            raise ValueError("STORAGE_BUCKET is required for S3 storage")
        return S3Storage(settings.storage_bucket, settings.storage_endpoint)
    return LocalStorage(settings.storage_local_path)


async def _write_bytes(path: Path, content: bytes) -> None:
    import asyncio

    await asyncio.to_thread(path.write_bytes, content)


async def _read_bytes(path: Path) -> bytes:
    import asyncio

    return await asyncio.to_thread(path.read_bytes)


async def _delete_file(path: Path) -> None:
    import asyncio

    await asyncio.to_thread(path.unlink)


async def _run_blocking(func, **kwargs):
    import asyncio

    return await asyncio.to_thread(func, **kwargs)
