from fastapi.testclient import TestClient


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Superuser"""
    login_data = {
        "username": 'superuser',
        "password": '12345678',
    }
    r = client.post('/token', data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_client1_token_headers(client: TestClient) -> dict[str, str]:
    """Confirmed client"""
    login_data = {
        "username": 'client1',
        "password": '123654789',
    }
    r = client.post('/token', data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_client2_token_headers(client: TestClient) -> dict[str, str]:
    """Unconfirmed client"""
    login_data = {
        "username": 'client2',
        "password": '123654789',
    }
    r = client.post('/token', data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
