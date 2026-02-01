import pytest


async def get_token(client, email="reviewer@test.com", password="Password123!"):
    await client.post("/api/v1/auth/signup", json={"email": email, "password": password, "role": "user"})
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_add_review(client):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/books",
        data={
            "title": "Review Book",
            "author": "Author",
            "genre": "Fantasy",
            "year_published": "2022",
        },
        files={"file": ("book.txt", b"Review content.", "text/plain")},
        headers=headers,
    )
    book_id = response.json()["id"]

    response = await client.post(f"/api/v1/books/{book_id}/borrow", headers=headers)
    assert response.status_code == 200

    response = await client.post(
        f"/api/v1/books/{book_id}/reviews",
        json={"review_text": "Great book!", "rating": 5},
        headers=headers,
    )
    assert response.status_code == 201

    response = await client.get(f"/api/v1/books/{book_id}/reviews")
    assert response.status_code == 200
    assert len(response.json()) == 1
