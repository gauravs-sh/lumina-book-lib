import base64

import pytest


@pytest.mark.asyncio
async def test_signup_and_login(client):
    payload = {"email": "user1@test.com", "password": "Password123!", "role": "user"}
    response = await client.post("/api/v1/auth/signup", json=payload)
    print('test_authhhhhhhhhhh1111:',response.json())
    assert response.json()["status"] == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user1@test.com", "password": "Password123!"},
    )

    print('test_authhhhhhhhhhh login_response:',login_response.json())
    
    assert login_response.json()["status"] == 200
    assert login_response.json()["data"]["access_token"]
