import base64

import pytest


@pytest.mark.asyncio
async def test_signup_and_login(client):
    payload = {"email": "user1@test.com", "password": "Password123!", "role": "user"}
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user1@test.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
