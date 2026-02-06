import pytest


async def get_token(client, email="booker@test.com", password="Password123!"):
    await client.post("/api/v1/auth/signup", json={"email": email, "password": password, "role": "user"})
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )

    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_create_book(client):
    token = await get_token(client, email="creator@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/books",
        data={
            "title": "Create Book",
            "author": "Author",
            "genre": "Nonfiction",
            "year_published": "2021",
        },
        files={"file": ("book.txt", b"Create book content.", "text/plain")},
        headers=headers,
    )

    assert response.json()["status"] == 201
    payload = response.json()["data"]
    assert payload["title"] == "Create Book"
    assert payload["file_name"] == "book.txt"


@pytest.mark.asyncio
async def test_book_crud(client):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/books",
        data={
            "title": "Test Book",
            "author": "Author",
            "genre": "Sci-Fi",
            "year_published": "2024",
        },
        files={"file": ("book.txt", b"This is a test book content.", "text/plain")},
        headers=headers,
    )

    assert response.json()["status"] == 201
    book_id = response.json()["data"]["id"]

    response = await client.get(f"/api/v1/books/{book_id}")
    assert response.json()["status"] == 200

    response = await client.post(f"/api/v1/books/{book_id}/borrow", headers=headers)
    assert response.json()["status"] == 200

    response = await client.post(f"/api/v1/books/{book_id}/return", headers=headers)
    assert response.json()["status"] == 200

    response = await client.get("/api/v1/books")
    assert response.json()["status"] == 200
    assert response.json()["data"]["items"]

    response = await client.get(f"/api/v1/books/{book_id}/summary")
    assert response.json()["status"] == 200

    response = await client.get(f"/api/v1/books/{book_id}/analysis")
    assert response.json()["status"] == 200

    response = await client.put(
        f"/api/v1/books/{book_id}",
        json={"genre": "Drama"},
        headers=headers,
    )
    assert response.json()["status"] == 200

    response = await client.delete(f"/api/v1/books/{book_id}", headers=headers)
    assert response.status_code == 204
