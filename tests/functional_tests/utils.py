from fastapi.testclient import TestClient


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": 'superuser',
        "password": '12345678',
    }
    r = client.post('/token', data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
