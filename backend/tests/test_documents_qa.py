import asyncio
import base64

import pytest


async def get_token(client, email="doc@test.com", password="Password123!"):
    await client.post("/api/v1/auth/signup", json={"email": email, "password": password, "role": "user"})
    credentials = base64.b64encode(f"{email}:{password}".encode("utf-8")).decode("utf-8")
    response = await client.post(
        "/api/v1/auth/token",
        headers={"Authorization": f"Basic {credentials}"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_document_ingestion_and_qa(client):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/documents",
        json={"filename": "doc.txt", "content": "FastAPI is a modern, fast web framework."},
        headers=headers,
    )
    doc_id = response.json()["id"]

    response = await client.post(f"/api/v1/ingestion/{doc_id}", headers=headers)
    assert response.status_code == 202

    await asyncio.sleep(0.2)

    response = await client.post(
        "/api/v1/qa",
        json={"question": "What is FastAPI?"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["answer"]
