import pytest


async def get_token(client, email="rec@test.com", password="Password123!"):
    await client.post("/api/v1/auth/signup", json={"email": email, "password": password, "role": "user"})
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_recommendations(client):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    for idx in range(3):
        await client.post(
            "/api/v1/books",
            data={
                "title": f"Book {idx}",
                "author": "Author",
                "genre": "Mystery" if idx % 2 == 0 else "Romance",
                "year_published": str(2020 + idx),
            },
            files={"file": (f"book-{idx}.txt", b"Some content", "text/plain")},
            headers=headers,
        )

    await client.put(
        "/api/v1/users/me/preferences",
        json={"preferences": {"genres": ["Mystery"]}},
        headers=headers,
    )

    response = await client.get("/api/v1/recommendations", headers=headers)
    assert response.json()["status"] == 200
    assert response.json()
