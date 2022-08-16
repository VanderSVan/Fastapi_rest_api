from tests.functional_tests.conftest import superuser_token
from tests.functional_tests.conftest import unconfirmed_client_token

from src.utils.response_generation.main import get_text
from src.utils.auth_utils.signature import Signer


class TestUser:
    # GET
    def test_get_me(self, client):
        response = client.get(
            f'/users/auth/me', headers=superuser_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']

    def test_get_confirmed_email(self, client):
        sign: str = Signer.sign_object({'username': 'client2'})
        response = client.get(
            f'/users/auth/confirm-email/{sign}/', headers=superuser_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json()['message'] == get_text('email_confirmed')

    def test_get_confirmed_reset_password(self, client):
        json_to_send: dict = {
            "password": "some_password",
            "password_confirm": "some_password"
        }
        sign: str = Signer.sign_object({'username': 'client1'})
        response = client.post(
            f'users/auth/confirm-reset-password/{sign}/',
            json=json_to_send,
            headers=superuser_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json()['message'] == get_text('changed_password')


class TestUserException:
    def test_request_from_non_confirmed_user(self, client):
        response_get_me = client.get(
            '/users/auth/me', headers=unconfirmed_client_token
        )
        response_reset_password = client.get(
            '/users/auth/reset-password/', headers=unconfirmed_client_token
        )
        responses: tuple = (response_get_me, response_reset_password)
        for response in responses:
            assert response.status_code == 401
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('email_not_confirmed')
