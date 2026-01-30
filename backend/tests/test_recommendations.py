import base64

import pytest


async def get_token(client, email="rec@test.com", password="Password123!"):
    await client.post("/api/v1/auth/signup", json={"email": email, "password": password, "role": "user"})
    credentials = base64.b64encode(f"{email}:{password}".encode("utf-8")).decode("utf-8")
    response = await client.post(
        "/api/v1/auth/token",
        headers={"Authorization": f"Basic {credentials}"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_recommendations(client):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    for idx in range(3):
        await client.post(
            "/api/v1/books",
            json={
                "title": f"Book {idx}",
                "author": "Author",
                "genre": "Mystery" if idx % 2 == 0 else "Romance",
                "year_published": 2020 + idx,
            },
            headers=headers,
        )

    response = await client.get("/api/v1/recommendations?genres=Mystery", headers=headers)
    assert response.status_code == 200
    assert response.json()
