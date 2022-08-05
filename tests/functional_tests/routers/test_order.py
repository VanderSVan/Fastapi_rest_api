import pytest

from src.utils.responses.main import get_text


class TestOrder:
    # GET
    def test_get_all_orders(self, client, superuser_token_headers):
        response = client.get(
            f'/orders/', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']

    @pytest.mark.parametrize("order_id", [1, 2, 3])
    def test_get_order_by_id(self, order_id, client, superuser_token_headers):
        response = client.get(
            f'/orders/{order_id}', headers=superuser_token_headers
        )
        response_id = response.json()['id']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_id == order_id

    @pytest.mark.parametrize("start_dt, number_of_orders", [
        ("2022-08-03", 2),
        ("2022-08-03T08:00", 2),
        ("2022-03-08", 3)
    ])
    def test_get_order_by_start_dt(self, start_dt, number_of_orders, client, superuser_token_headers):
        response = client.get(
            f'/orders/?start_datetime={start_dt}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("end_dt, number_of_orders", [
        ("2022-08-03", 3),
        ("2022-08-03T08:00", 1),
        ("2022-03-08", 1)
    ])
    def test_get_order_by_end_dt(self, end_dt, number_of_orders, client, superuser_token_headers):
        response = client.get(
            f'/orders/?end_datetime={end_dt}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("start_dt, end_dt, number_of_orders", [
        ("2022-08-03", "2022-08-03", 2),
        ("2022-08-03T15:00", "2022-08-03T16:00", 1),
        ("2022-01-01", "2022-12-31", 3)
    ])
    def test_get_order_by_start_end_dt(self, start_dt, end_dt, number_of_orders, client, superuser_token_headers):
        response = client.get(
            f'/orders/?start_datetime={start_dt}&end_datetime={end_dt}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("status, number_of_orders", [
        ("processing", 1),
        ("confirmed", 2)
    ])
    def test_get_order_by_status(self, status, number_of_orders, client, superuser_token_headers):
        response = client.get(
            f'/orders/?status={status}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("user_id, number_of_orders", [
        (2, 1),
        (3, 1),
        (4, 1)
    ])
    def test_get_order_by_user_id(self, user_id, number_of_orders, client, superuser_token_headers):
        response = client.get(
            f'/orders/?user_id={user_id}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    # DELETE
    def test_delete_order_by_id(self, client, superuser_token_headers):
        response = client.delete(
            '/orders/2', headers=superuser_token_headers
        )
        response_msg = response.json()['message']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_msg == get_text('delete').format('order', 2)

    # PATCH
    @pytest.mark.parametrize("order_id, json_to_send, result_json", [
        (
                1,
                {
                    "status": "confirmed",
                    "add_tables": [2, 3, 4, 5],
                    "delete_tables": [1, 2, 6]
                },
                {'message': get_text("patch").format('order', 1)}
        )
    ])
    def test_patch_order_by_id(self, order_id, json_to_send, result_json, client, superuser_token_headers):
        response = client.patch(
            f'/orders/{order_id}', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    # POST
    @pytest.mark.parametrize("json_to_send, result_json", [
        (
                {
                    "start_datetime": "2022-08-04T10:00",
                    "end_datetime": "2022-08-04T11:59",
                    "user_id": 1,
                    "tables": [
                        1, 2, 3, 4
                    ]
                },
                {
                    'message': get_text("post").format('order', 4)
                }
        )
    ])
    def test_post_order(self, json_to_send, result_json, client, superuser_token_headers):
        response = client.post(
            '/orders/create', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == 201
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json


class TestOrderException:
    @pytest.mark.parametrize("order_id, json_to_send, result_json, status", [
        # give equal fields start and end datetime
        (
                1,
                {
                    "start_datetime": "2022-08-05T07:00",
                    "end_datetime": "2022-08-05T07:00",
                },
                {'message': get_text("order_err_start_equal_end")},
                400
        ),
        # give end datetime that equal start datetime
        (
                2,
                {"end_datetime": "2022-08-03T15:00"},
                {'message': get_text("order_err_start_equal_end")},
                400
        ),
        # instead of the fields 'add_tables' or 'delete_tables' give 'tables'
        (
                3,
                {'tables': [1, 2, 3]},
                {'message': get_text("err_patch_no_data")},
                400
        ),
        # give wrong table ids for add
        (
                1,
                {
                    "add_tables": [
                        1, 200, 300
                    ]
                },
                {'message': get_text("not_found").format('table', '200')},
                404
        ),
        # give wrong table ids for delete
        (
                1,
                {
                    "delete_tables": [
                        1, 200, 300
                    ]
                },
                {'message': get_text("patch").format('order', '1')},
                200
        ),
        # give wrong user_id
        pytest.param(
            3,
            {'user_id': 10},
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about non-existent key value 'user_id' = '10'"}
            },
            400,
            marks=pytest.mark.xfail(reason="non-existent key value 'user_id' = '10'")
        ),
    ])
    def test_patch_wrong_order(self, order_id, json_to_send, result_json, status, client, superuser_token_headers):
        response = client.patch(
            f'/orders/{order_id}', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == status
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    @pytest.mark.parametrize("json_to_send, result_json, status", [
        # give equal fields start and end datetime
        (
                {
                    "start_datetime": "2022-08-05T10:00",
                    "end_datetime": "2022-08-05T10:00",
                    "user_id": 1,
                    "tables": [
                        1, 2, 3
                    ]
                },
                {'message': get_text("order_err_start_equal_end")},
                400
        ),
        # give wrong table ids
        (
                {
                    "start_datetime": "2022-08-05T10:00",
                    "end_datetime": "2022-08-05T11:00",
                    "user_id": 1,
                    "tables": [
                        1, 200, 300
                    ]
                },
                {'message': get_text("not_found").format('table', '200')},
                404
        ),
        # give wrong user_id
        pytest.param(
            {
                "start_datetime": "2022-08-05T10:00",
                "end_datetime": "2022-08-05T11:00",
                "user_id": 100,
                "tables": [
                    1, 2, 3
                ]
            },
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about non-existent key value 'user_id' = '100'"}
            },
            400,
            marks=pytest.mark.xfail(reason="non-existent key value 'user_id' = '100'")
        ),
    ])
    def test_post_wrong_order(self, json_to_send, result_json, status, client, superuser_token_headers):
        response = client.post(
            '/orders/create', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == status
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    @pytest.mark.parametrize("json_to_send", [
        {
            "status": "confirmed",
            "add_tables": [2, 3, 4, 5],
            "delete_tables": [1, 2, 6]
        }
    ])
    def test_forbidden_request(self, json_to_send, client, confirmed_client_token_headers):
        response_delete = client.delete(
            '/orders/1', headers=confirmed_client_token_headers
        )
        response_patch = client.patch(
            '/orders/1', json=json_to_send, headers=confirmed_client_token_headers
        )
        responses: tuple = (response_delete, response_patch)
        for response in responses:
            assert response.status_code == 404
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('not_found').format('order', 1)
