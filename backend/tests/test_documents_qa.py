import asyncio
import pytest


async def get_token(client, email="doc@test.com", password="Password123!"):
    await client.post("/api/v1/auth/signup", json={"email": email, "password": password, "role": "user"})
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_document_ingestion_and_qa(client):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/documents",
        json={"filename": "doc.txt", "content": "FastAPI is a modern, fast web framework."},
        headers=headers,
    )
    doc_id = response.json()["data"]["id"]

    response = await client.post(f"/api/v1/ingestion/{doc_id}", headers=headers)
    assert response.json()["status"] == 202

    await asyncio.sleep(0.2)

    response = await client.post(
        "/api/v1/qa",
        json={"question": "What is FastAPI?"},
        headers=headers,
    )

    print('ingestion response::::',response.json())
    assert response.json()["status"] == 200
    assert response.json()["data"]["answer"]
