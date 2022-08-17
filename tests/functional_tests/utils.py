from fastapi.testclient import TestClient

from tests.functional_tests.test_data import users_json

superuser: dict = {
    'username': users_json[0]['username'],
    'password': users_json[0]['password']
}
admin: dict = {
    'username': users_json[1]['username'],
    'password': users_json[1]['password']
}
client_1: dict = {
    'username': users_json[2]['username'],
    'password': users_json[2]['password']
}
client_2: dict = {
    'username': users_json[3]['username'],
    'password': users_json[3]['password']
}


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Superuser"""
    login_data: dict = superuser
    r = client.post('/token', data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_admin_token_headers(client: TestClient) -> dict[str, str]:
    """Admin"""
    login_data: dict = admin
    r = client.post('/token', data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_client1_token_headers(client: TestClient) -> dict[str, str]:
    """Confirmed client"""
    login_data: dict = client_1
    r = client.post('/token', data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_client2_token_headers(client: TestClient) -> dict[str, str]:
    """Unconfirmed client"""
    login_data: dict = client_2
    r = client.post('/token', data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
