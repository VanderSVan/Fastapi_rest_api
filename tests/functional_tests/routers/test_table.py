import pytest

from src.utils.response_generation.main import get_text


class TestTable:
    # GET
    def test_get_all_tables(self, client, superuser_token_headers):
        response = client.get(
            f'/tables/', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']

    @pytest.mark.parametrize("table_id, number_of_seats", [
        (1, 6),
        (4, 3),
        (6, 15)
    ])
    def test_get_table_by_id(self, table_id, number_of_seats, client, superuser_token_headers):
        response = client.get(
            f'/tables/{table_id}', headers=superuser_token_headers
        )
        output_number_of_seats = response.json()['number_of_seats']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert number_of_seats == output_number_of_seats

    @pytest.mark.parametrize("table_type, number_of_tables", [
        ('standard', 2),
        ('private', 2),
        ('vip_room', 2)
    ])
    def test_get_by_type(self, table_type, number_of_tables, client, superuser_token_headers):
        response = client.get(
            f'/tables/?type={table_type}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_tables

    @pytest.mark.parametrize("number_of_seats, number_of_tables", [
        (6, 4),
        (12, 5),
        (15, 6)
    ])
    def test_get_by_number_of_seats(self, number_of_seats, number_of_tables, client, superuser_token_headers):
        response = client.get(
            f'/tables/?number_of_seats={number_of_seats}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_tables

    @pytest.mark.parametrize("price_per_hour, number_of_tables", [
        (3000.00, 3),
        (4000.00, 4),
        (15555.55, 6)
    ])
    def test_get_by_price_per_hour(self, price_per_hour, number_of_tables, client, superuser_token_headers):
        response = client.get(
            f'/tables/?price_per_hour={price_per_hour}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_tables

    # DELETE
    def test_delete_table_by_id(self, client, superuser_token_headers):
        response = client.delete(
            '/tables/6', headers=superuser_token_headers
        )
        response_msg = response.json()['message']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_msg == get_text('delete').format('table', 6)

    # PATCH
    @pytest.mark.parametrize("table_id, json_to_send, result_json", [
        (
                1,
                {
                    "type": "private",
                    "price_per_hour": 3000
                },
                {
                    'message': get_text("patch").format('table', 1)
                }
        )
    ])
    def test_patch_table_by_id(self, table_id, json_to_send, result_json, client, superuser_token_headers):
        response = client.patch(
            f'/tables/{table_id}', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json
        
    # POST
    @pytest.mark.parametrize("json_to_send, result_json", [
        (
                {
                    "type": "vip_room",
                    "number_of_seats": 8,
                    "price_per_hour": 30000
                },
                {
                    'message': get_text("post").format('table', 7)
                }
        )
    ])
    def test_post_table(self, json_to_send, result_json, client, superuser_token_headers):
        response = client.post(
            '/tables/create', json=json_to_send, headers=superuser_token_headers
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
    def test_forbidden_request(self, patch_json_to_send, post_json_to_send, client, confirmed_client_token_headers):
        response_delete = client.delete(
            '/tables/1', headers=confirmed_client_token_headers
        )
        response_patch = client.patch(
            '/tables/1', json=patch_json_to_send, headers=confirmed_client_token_headers
        )
        response_post = client.patch(
            '/tables/1', json=post_json_to_send, headers=confirmed_client_token_headers
        )
        responses: tuple = (response_delete, response_patch, response_post)
        for response in responses:
            assert response.status_code == 403
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('forbidden_request')

