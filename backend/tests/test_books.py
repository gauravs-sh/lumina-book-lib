import base64

import pytest


async def get_token(client, email="booker@test.com", password="Password123!"):
    await client.post("/api/v1/auth/signup", json={"email": email, "password": password, "role": "user"})
    credentials = base64.b64encode(f"{email}:{password}".encode("utf-8")).decode("utf-8")
    response = await client.post(
        "/api/v1/auth/token",
        headers={"Authorization": f"Basic {credentials}"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_book_crud(client):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/books",
        json={
            "title": "Test Book",
            "author": "Author",
            "genre": "Sci-Fi",
            "year_published": 2024,
            "content": "This is a test book content.",
        },
        headers=headers,
    )
    assert response.status_code == 201
    book_id = response.json()["id"]

    response = await client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200

    response = await client.put(
        f"/api/v1/books/{book_id}",
        json={"genre": "Drama"},
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.delete(f"/api/v1/books/{book_id}", headers=headers)
    assert response.status_code == 204
