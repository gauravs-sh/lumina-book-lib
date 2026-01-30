import base64

import pytest


@pytest.mark.asyncio
async def test_signup_and_login(client):
    payload = {"email": "user1@test.com", "password": "Password123!", "role": "user"}
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201

    credentials = base64.b64encode(b"user1@test.com:Password123!").decode("utf-8")
    response = await client.post(
        "/api/v1/auth/token",
        headers={"Authorization": f"Basic {credentials}"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
