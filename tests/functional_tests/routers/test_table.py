import pytest

from tests.functional_tests.conftest import (superuser_token,
                                             admin_token,
                                             confirmed_client_token,
                                             unconfirmed_client_token)
from tests.functional_tests.test_data import tables_json

from src.utils.response_generation.main import get_text


class TestTable:
    # GET
    def test_get_all_tables(self, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/tables/', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == len(tables_json)

            for table in response.json():
                cost = table['orders'][0]['cost']
                id_ = table['orders'][0]['id']
                status = table['orders'][0]['status']
                user_id = table['orders'][0]['user_id']

                if token is confirmed_client_token:
                    assert cost is None
                    assert id_ is None
                    assert status is None
                    assert user_id is None
                else:
                    assert cost is not None
                    assert id_ is not None
                    assert status is not None
                    assert user_id is not None

    @pytest.mark.parametrize("table_id, number_of_seats", [
        (1, 6),
        (4, 3),
        (6, 15)
    ])
    def test_get_table_by_id(self, table_id, number_of_seats, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/tables/{table_id}', headers=token
            )
            output_number_of_seats = response.json()['number_of_seats']
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert number_of_seats == output_number_of_seats

            cost = response.json()['orders'][0]['cost']
            id_ = response.json()['orders'][0]['id']
            status = response.json()['orders'][0]['status']
            user_id = response.json()['orders'][0]['user_id']

            if token is confirmed_client_token:
                assert cost is None
                assert id_ is None
                assert status is None
                assert user_id is None
            else:
                assert cost is not None
                assert id_ is not None
                assert status is not None
                assert user_id is not None

    @pytest.mark.parametrize("table_type, number_of_tables", [
        ('standard', 2),
        ('private', 2),
        ('vip_room', 2)
    ])
    def test_get_by_type(self, table_type, number_of_tables, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/tables/?type={table_type}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_tables

    @pytest.mark.parametrize("number_of_seats, number_of_tables", [
        (6, 4),
        (12, 5),
        (15, 6)
    ])
    def test_get_by_number_of_seats(self, number_of_seats, number_of_tables, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/tables/?number_of_seats={number_of_seats}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_tables

    @pytest.mark.parametrize("price_per_hour, number_of_tables", [
        (3000.00, 3),
        (4000.00, 4),
        (15555.55, 6)
    ])
    def test_get_by_price_per_hour(self, price_per_hour, number_of_tables, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/tables/?price_per_hour={price_per_hour}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_tables

    @pytest.mark.parametrize("start_dt, number_of_tables", [
        ("2022-08-03", 4),
        ("2022-08-03T15:00", 3),
        ("2022-03-08", 6)
    ])
    def test_get_by_start_dt(self, start_dt, number_of_tables, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'/tables/?start_datetime={start_dt}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_tables

    @pytest.mark.parametrize("end_dt, number_of_tables", [
        ("2022-08-03", 6),
        ("2022-08-03T08:00", 3),
        ("2022-03-08", 3)
    ])
    def test_get_by_end_dt(self, end_dt, number_of_tables, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'/tables/?end_datetime={end_dt}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_tables

    @pytest.mark.parametrize("start_dt, end_dt, number_of_tables", [
        ("2022-08-03", "2022-08-03", 4),
        ("2022-08-03T15:00", "2022-08-03T16:00", 3),
        ("2022-08-03T08:30", "2022-08-03T09:00", 1),
        ("2022-01-01", "2022-12-31", 6)
    ])
    def test_get_by_start_end_dt(self, start_dt, end_dt, number_of_tables, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'/tables/?start_datetime={start_dt}&end_datetime={end_dt}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_tables

    # DELETE
    @pytest.mark.parametrize('token', [superuser_token, admin_token])
    def test_delete_table_by_id(self, token, client):
        response = client.delete(
            '/tables/6', headers=token
        )
        response_msg = response.json()['message']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_msg == get_text('delete').format('table', 6)

    # PATCH
    @pytest.mark.parametrize("table_id, json_to_send, result_json, token", [
        (
                1,
                {
                    "type": "private",
                    "price_per_hour": 3000
                },
                {'message': get_text("patch").format('table', 1)},
                superuser_token
        ),
        (
                1,
                {
                    "type": "private",
                    "price_per_hour": 3000
                },
                {'message': get_text("patch").format('table', 1)},
                admin_token
        )
    ])
    def test_patch_table_by_id(self, table_id, json_to_send, result_json, token, client):
        response = client.patch(
            f'/tables/{table_id}', json=json_to_send, headers=token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json
        
    # POST
    @pytest.mark.parametrize("json_to_send, result_json, token", [
        (
                {
                    "type": "vip_room",
                    "number_of_seats": 8,
                    "price_per_hour": 30000
                },
                {'message': get_text("post").format('table', 7)},
                superuser_token
        ),
        (
                {
                    "type": "vip_room",
                    "number_of_seats": 8,
                    "price_per_hour": 30000
                },
                {'message': get_text("post").format('table', 7)},
                admin_token
        )
    ])
    def test_post_table(self, json_to_send, result_json, token, client):
        response = client.post(
            '/tables/create', json=json_to_send, headers=token
        )
        assert response.status_code == 201
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json
        
        
class TestTableException:
    @pytest.mark.parametrize("patch_json_to_send, post_json_to_send", [
        (
            {
                "type": "private",
                "price_per_hour": 3000
            },
            {
                "type": "vip_room",
                "number_of_seats": 8,
                "price_per_hour": 30000
            }
        )

    ])
    def test_forbidden_request(self, patch_json_to_send, post_json_to_send, client):
        response_delete = client.delete(
            '/tables/1', headers=confirmed_client_token
        )
        response_patch = client.patch(
            '/tables/1', json=patch_json_to_send, headers=confirmed_client_token
        )
        response_post = client.post(
            '/tables/create', json=post_json_to_send, headers=confirmed_client_token
        )
        responses: tuple = (response_delete, response_patch, response_post)
        for response in responses:
            assert response.status_code == 403
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('forbidden_request')

    @pytest.mark.parametrize("json_to_send", [
            {
                "type": "standard",
                "number_of_seats": 4,
                "price_per_hour": 5000
            },
    ])
    def test_not_confirmed_request(self, json_to_send, client):
        response_get = client.get(
            '/tables/', headers=unconfirmed_client_token
        )
        response_get_by_id = client.get(
            '/tables/1', headers=unconfirmed_client_token
        )
        response_delete = client.delete(
            '/tables/1', headers=unconfirmed_client_token
        )
        response_patch = client.patch(
            '/tables/1', json=json_to_send, headers=unconfirmed_client_token
        )
        response_post = client.post(
            '/tables/create', json=json_to_send, headers=unconfirmed_client_token
        )
        responses: tuple = (response_get, response_get_by_id, response_delete, response_patch, response_post)
        for response in responses:
            assert response.status_code == 401
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('email_not_confirmed')
