import pytest

from tests.functional_tests.conftest import superuser_token
from tests.functional_tests.conftest import confirmed_client_token

from src.utils.response_generation.main import get_text


class TestUser:
    # GET
    def test_get_all_users(self, client):
        response = client.get(
            f'/users/', headers=superuser_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']

    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_get_user_by_id(self, user_id, client):
        response = client.get(
            f'/users/{user_id}', headers=superuser_token
        )
        response_id = response.json()['id']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_id == user_id

    @pytest.mark.parametrize("phone, username", [
        ('0123456789', 'admin'),
        ('147852369', 'client1'),
        ('1478523690', 'client2')
    ])
    def test_get_user_by_phone(self, phone, username, client):
        response = client.get(
            f'/users/?phone={phone}', headers=superuser_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json()[0]['username'] == username

    @pytest.mark.parametrize("status, number_of_users", [
        ("unconfirmed", 1),
        ("confirmed", 3)
    ])
    def test_get_user_by_status(self, status, number_of_users, client):
        response = client.get(
            f'/users/?status={status}', headers=superuser_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_users

    # DELETE
    def test_delete_user_by_id(self, client):
        response = client.delete(
            '/users/4', headers=superuser_token
        )
        response_msg = response.json()['message']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_msg == get_text('delete').format('user', 4)

    # PATCH
    @pytest.mark.parametrize("user_id, json_to_send, result_json", [
        (
                4,
                {
                    "status": "confirmed",
                    "phone": "875726804043761"
                },
                {'message': get_text("patch").format('user', 4)}
        )
    ])
    def test_patch_user_by_id(self, user_id, json_to_send, result_json, client):
        response = client.patch(
            f'/users/{user_id}', json=json_to_send, headers=superuser_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    # POST
    @pytest.mark.parametrize("json_to_send, result_json", [
        (
                {
                    "username": "new_client",
                    "email": "new_client@example.com",
                    "phone": "715471115783477",
                    "role": "client",
                    "password": "stringst123/"
                },
                {
                    'message': get_text("post").format('user', 5)
                }
        )
    ])
    def test_post_user(self, json_to_send, result_json, client):
        response = client.post(
            '/users/create', json=json_to_send, headers=superuser_token
        )
        assert response.status_code == 201
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json


class TestUserException:
    @pytest.mark.parametrize("user_id, json_to_send, result_json, status", [
        # give existent username
        pytest.param(
            4,
            {
                "username": "client1"
            },
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about repeated key value 'username' = 'client1'"}
            },
            400,
            marks=pytest.mark.xfail(reason="'username' = 'client1' already exists")
        ),
        # give existent email
        pytest.param(
            4,
            {
                "email": "client1@example.com"
            },
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about repeated key value 'email': 'client1@example.com'"}
            },
            400,
            marks=pytest.mark.xfail(reason="'email' = 'client1@example.com' already exists")
        ),
        # give existent phone
        pytest.param(
            4,
            {
                "phone": "147852369"
            },
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about repeated key value 'phone': '147852369'"}
            },
            400,
            marks=pytest.mark.xfail(reason="'phone' = '147852369' already exists")
        ),
    ])
    def test_patch_wrong_user(self, user_id, json_to_send, result_json, status, client):
        response = client.patch(
            f'/users/{user_id}', json=json_to_send, headers=superuser_token
        )
        assert response.status_code == status
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    @pytest.mark.parametrize("json_to_send, result_json, status", [
        # give existent username
        pytest.param(
            {
                "username": "client1",
                "email": "user@example.com",
                "phone": "907415594679555",
                "role": "superuser",
                "password": "stringst"
            },
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about repeated key value 'username' = 'client1'"}
            },
            400,
            marks=pytest.mark.xfail(reason="'username' = 'client1' already exists")
        ),
        # give existent email
        pytest.param(
            {
                "username": "some_client",
                "email": "client1@example.com",
                "phone": "907415594679555",
                "role": "superuser",
                "password": "stringst"
            },
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about repeated key value 'email': 'client1@example.com'"}
            },
            400,
            marks=pytest.mark.xfail(reason="'email' = 'client1@example.com' already exists")
        ),
        # give existent phone
        pytest.param(
            {
                "username": "string",
                "email": "user@example.com",
                "phone": "147852369",
                "role": "superuser",
                "password": "stringst"
            },
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about repeated key value 'phone': '147852369'"}
            },
            400,
            marks=pytest.mark.xfail(reason="'phone' = '147852369' already exists")
        ),
    ])
    def test_post_wrong_user(self, json_to_send, result_json, status, client):
        response = client.post(
            f'/users/create', json=json_to_send, headers=superuser_token
        )
        assert response.status_code == status
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    @pytest.mark.parametrize("json_to_send", [
        (
            {
                "username": "string",
                "email": "user@example.com",
                "phone": "907415594679555",
                "role": "superuser",
                "password": "stringst"
            }
        )
    ])
    def test_forbidden_request(self, json_to_send, client):
        response_get = client.get(
            '/users/', headers=confirmed_client_token
        )
        response_get_id = client.get(
            '/users/4', headers=confirmed_client_token
        )
        response_delete = client.delete(
            '/users/4', headers=confirmed_client_token
        )
        response_patch = client.patch(
            '/users/4', json=json_to_send, headers=confirmed_client_token
        )
        response_post = client.post(
            '/users/create', json=json_to_send, headers=confirmed_client_token
        )
        responses: tuple = (response_get, response_get_id, response_delete, response_patch, response_post)
        for response in responses:
            assert response.status_code == 403
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('forbidden_request')
