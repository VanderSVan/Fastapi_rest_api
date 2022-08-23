import pytest

from tests.functional_tests.test_data import order_json
from tests.functional_tests.conftest import (api_url,
                                             superuser_token,
                                             admin_token,
                                             confirmed_client_token,
                                             unconfirmed_client_token)

from src.utils.response_generation.main import get_text


class TestOrderViaSuperUserOrAdmin:
    # GET
    @pytest.mark.parametrize('token', [superuser_token, admin_token])
    def test_get_all_orders(self, token, client):
        response = client.get(
            f'{api_url}/orders/', headers=token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == 3

    @pytest.mark.parametrize("order_id", [1, 2, 3])
    def test_get_order_by_id(self, order_id, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'{api_url}/orders/{order_id}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']

            # process data to compare
            response_without_tables = {k: v for k, v in response.json().items() if k != 'tables'}
            data_to_compare = {k: v for k, v in order_json[order_id - 1].items() if k != 'tables'}

            assert response_without_tables == data_to_compare

    @pytest.mark.parametrize("start_dt, number_of_orders", [
        ("2022-08-03", 2),
        ("2022-08-03T15:00", 1),
        ("2022-03-08", 3)
    ])
    def test_get_order_by_start_dt(self, start_dt, number_of_orders, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'{api_url}/orders/?start_datetime={start_dt}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("end_dt, number_of_orders", [
        ("2022-08-03", 3),
        ("2022-08-03T08:00", 1),
        ("2022-03-08", 1)
    ])
    def test_get_order_by_end_dt(self, end_dt, number_of_orders, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'{api_url}/orders/?end_datetime={end_dt}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("start_dt, end_dt, number_of_orders", [
        ("2022-08-03", "2022-08-03", 2),
        ("2022-08-03T15:00", "2022-08-03T16:00", 1),
        ("2022-01-01", "2022-12-31", 3)
    ])
    def test_get_order_by_start_end_dt(self, start_dt, end_dt, number_of_orders, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'{api_url}/orders/?start_datetime={start_dt}&end_datetime={end_dt}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("status, number_of_orders", [
        ("processing", 1),
        ("confirmed", 2)
    ])
    def test_get_order_by_status(self, status, number_of_orders, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'{api_url}/orders/?status={status}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("user_id, number_of_orders", [
        (2, 1),
        (3, 1),
        (4, 1)
    ])
    def test_get_order_by_user_id(self, user_id, number_of_orders, client):
        for token in superuser_token, admin_token:
            response = client.get(
                f'{api_url}/orders/?user_id={user_id}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_orders

    # DELETE
    @pytest.mark.parametrize('order_id, result_msg, status, token', [
        # superuser
        (1, get_text('delete').format('order', 1), 200, superuser_token),
        (2, get_text('delete').format('order', 2), 200, superuser_token),
        (10, get_text('not_found').format('order', 10), 404, superuser_token),
        # admin
        (1, get_text('delete').format('order', 1), 200, admin_token),
        (2, get_text('delete').format('order', 2), 200, admin_token),
        (10, get_text('not_found').format('order', 10), 404, admin_token)
    ])
    def test_delete_order_by_id(self, order_id, result_msg, status, token, client):
        before_delete_response = client.get(
            f'{api_url}/orders/{order_id}', headers=token
        )
        main_response = client.delete(
            f'{api_url}/orders/{order_id}', headers=token
        )
        after_delete_response = client.get(
            f'{api_url}/orders/{order_id}', headers=token
        )
        response_msg = main_response.json()['message']
        assert main_response.status_code == status
        assert 'application/json' in main_response.headers['Content-Type']
        assert response_msg == result_msg
        if status == 200:
            assert before_delete_response is not None
            assert after_delete_response.json() is None

    # PATCH
    @pytest.mark.parametrize("order_id, json_to_send, result_json, token", [
        # superuser
        (
                1,
                {
                    "status": "confirmed",
                    "add_tables": [2, 3, 4, 5],
                    "delete_tables": [1, 2, 6]
                },
                {'message': get_text("patch").format('order', 1)},
                superuser_token,
        ),
        # admin
        (
                1,
                {
                    "status": "confirmed",
                    "add_tables": [2, 3, 4, 5],
                    "delete_tables": [1, 2, 6]
                },
                {'message': get_text("patch").format('order', 1)},
                admin_token,
        )
    ])
    def test_patch_order_by_id(self, order_id, json_to_send, result_json, token, client):
        before_patch_response = client.get(
            f'{api_url}/orders/{order_id}', headers=token
        )
        main_response = client.patch(
            f'{api_url}/orders/{order_id}', json=json_to_send, headers=token
        )
        after_patch_response = client.get(
            f'{api_url}/orders/{order_id}', headers=token
        )
        # process data to compare
        table_ids_before_patch = [
            [table['id'] for table in v]
            for k, v in before_patch_response.json().items()
            if k == 'tables'
        ]
        table_ids_after_patch = [
            [table['id'] for table in v]
            for k, v in after_patch_response.json().items()
            if k == 'tables'
        ]
        assert main_response.status_code == 200
        assert 'application/json' in main_response.headers['Content-Type']
        assert main_response.json() == result_json
        assert table_ids_before_patch != table_ids_after_patch
        assert table_ids_before_patch[0] == [6]
        assert table_ids_after_patch[0] == [2, 3, 4, 5]

    # POST
    @pytest.mark.parametrize("json_to_send, result_json, token", [
        # superuser
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
                },
                superuser_token
        ),
        # admin
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
                },
                admin_token
        )
    ])
    def test_post_order(self, json_to_send, result_json, token, client):
        before_post_response = client.get(
            f'{api_url}/orders/', headers=token
        )
        main_response = client.post(
            f'{api_url}/orders/create', json=json_to_send, headers=token
        )
        after_post_response = client.get(
            f'{api_url}/orders/', headers=token
        )
        assert main_response.status_code == 201
        assert 'application/json' in main_response.headers['Content-Type']
        assert main_response.json() == result_json
        assert len(before_post_response.json()) != len(after_post_response.json())


class TestOrderViaConfirmedUser:
    # GET
    def test_get_all_orders(self, client):
        response = client.get(
            f'{api_url}/orders/', headers=confirmed_client_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == 1

    @pytest.mark.parametrize("order_id, result_order_id", [
        (1, None),
        (2, 2),
        (3, None)
    ])
    def test_get_order_by_id(self, order_id, result_order_id, client):
        response = client.get(
            f'{api_url}/orders/{order_id}', headers=confirmed_client_token
        )
        response_id = response.json()['id'] if response.json() else None
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_id == result_order_id

        if response_id:
            response_without_tables = {k: v for k, v in response.json().items() if k != 'tables'}
            data_to_compare = {k: v for k, v in order_json[order_id - 1].items() if k != 'tables'}

            assert response_without_tables == data_to_compare

    @pytest.mark.parametrize("start_dt, number_of_orders", [
        ("2022-08-03", 1),
        ("2022-08-03T08:00", 1),
        ("2022-03-08", 1)
    ])
    def test_get_order_by_start_dt(self, start_dt, number_of_orders, client):
        response = client.get(
            f'{api_url}/orders/?start_datetime={start_dt}', headers=confirmed_client_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("end_dt, number_of_orders", [
        ("2022-08-03", 1),
        ("2022-08-03T08:00", 0),
        ("2022-03-08", 0)
    ])
    def test_get_order_by_end_dt(self, end_dt, number_of_orders, client):
        response = client.get(
            f'{api_url}/orders/?end_datetime={end_dt}', headers=confirmed_client_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("start_dt, end_dt, number_of_orders", [
        ("2022-08-03", "2022-08-03", 1),
        ("2022-08-03T15:00", "2022-08-03T16:00", 1),
        ("2022-01-01", "2022-12-31", 1)
    ])
    def test_get_order_by_start_end_dt(self, start_dt, end_dt, number_of_orders, client):
        response = client.get(
            f'{api_url}/orders/?start_datetime={start_dt}&end_datetime={end_dt}', headers=confirmed_client_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("status, number_of_orders", [
        ("processing", 0),
        ("confirmed", 1)
    ])
    def test_get_order_by_status(self, status, number_of_orders, client):
        response = client.get(
            f'{api_url}/orders/?status={status}', headers=confirmed_client_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_orders

    @pytest.mark.parametrize("user_id, result_user_id", [
        (2, 3),
        (3, 3),
        (4, 3)
    ])
    def test_get_order_by_user_id(self, user_id, result_user_id, client):
        response = client.get(
            f'{api_url}/orders/?user_id={user_id}', headers=confirmed_client_token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        for order in response.json():
            assert order['user_id'] == result_user_id

    # DELETE
    @pytest.mark.parametrize('order_id, result_msg, status', [
        (1, get_text('not_found').format('order', 1), 404),
        (2, get_text('delete').format('order', 2), 200),
        (3, get_text('not_found').format('order', 3), 404)
    ])
    def test_delete_order_by_id(self, order_id, result_msg, status, client):
        before_delete_response = client.get(
            f'{api_url}/orders/{order_id}', headers=confirmed_client_token
        )
        main_response = client.delete(
            f'{api_url}/orders/{order_id}', headers=confirmed_client_token
        )
        after_delete_response = client.get(
            f'{api_url}/orders/{order_id}', headers=confirmed_client_token
        )
        response_msg = main_response.json()['message']
        assert main_response.status_code == status
        assert 'application/json' in main_response.headers['Content-Type']
        assert response_msg == result_msg
        if status == 200:
            assert before_delete_response is not None
            assert after_delete_response.json() is None

    # PATCH
    @pytest.mark.parametrize("order_id, json_to_send, result_json, status", [
        (
                2,
                {
                    "start_datetime": "2022-08-08T14:01",
                    "end_datetime": "2022-08-08T14:59",
                    "add_tables": [2, 3, 4, 5],
                    "delete_tables": [1, 2, 6]
                },
                {'message': get_text("patch").format('order', 2)},
                200
        ),
        (
                1,
                {
                    "add_tables": [2, 3, 4, 5],
                    "delete_tables": [1, 2, 6]
                },
                {'message': get_text("not_found").format('order', 1)},
                404
        )
    ])
    def test_patch_order_by_id(self, order_id, json_to_send, result_json, status, client):
        before_patch_response = client.get(
            f'{api_url}/orders/{order_id}', headers=superuser_token
        )
        main_response = client.patch(
            f'{api_url}/orders/{order_id}', json=json_to_send, headers=confirmed_client_token
        )
        after_patch_response = client.get(
            f'{api_url}/orders/{order_id}', headers=superuser_token
        )
        # process data to compare
        table_ids_before_patch = [
            [table['id'] for table in v]
            for k, v in before_patch_response.json().items()
            if k == 'tables'
        ]
        table_ids_after_patch = [
            [table['id'] for table in v]
            for k, v in after_patch_response.json().items()
            if k == 'tables'
        ]
        assert main_response.status_code == status
        assert 'application/json' in main_response.headers['Content-Type']
        assert main_response.json() == result_json
        if status == 200:
            assert table_ids_before_patch != table_ids_after_patch
            assert table_ids_before_patch[0] == [1, 2, 3]
            assert table_ids_after_patch[0] == [2, 3, 4, 5]

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
    def test_post_order(self, json_to_send, result_json, client):
        before_post_response = client.get(
            f'{api_url}/orders/', headers=superuser_token
        )
        main_response = client.post(
            f'{api_url}/orders/create', json=json_to_send, headers=confirmed_client_token
        )
        after_post_response = client.get(
            f'{api_url}/orders/', headers=superuser_token
        )
        assert main_response.status_code == 201
        assert 'application/json' in main_response.headers['Content-Type']
        assert main_response.json() == result_json
        assert len(before_post_response.json()) != len(after_post_response.json())


class TestOrderException:
    # PATCH
    @pytest.mark.parametrize("order_id, json_to_send, result_json, status", [
        # give equal fields start and end datetime
        (
                2,
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
        # give end datetime which is less than start datetime
        (
                2,
                {"end_datetime": "2022-08-03T14:00"},
                {'message': get_text("order_err_end_less_start")},
                400
        ),
        # give a different day for the end datetime than the start datetime
        (
                2,
                {"end_datetime": "2022-08-04T15:00"},
                {'message': get_text("order_err_not_same_day")},
                400
        ),
        # give a datetime range that is inside the break time range
        (
                2,
                {
                    "start_datetime": "2022-08-11T11:00",
                    "end_datetime": "2022-08-11T12:30"
                },
                {'message': get_text("time_inside_break").format('2022-08-11T12:00:00 - 2022-08-11T12:59:59')},
                400
        ),
        # give a datetime range that is outside the time range of the daily schedule
        (
                2,
                {
                    "start_datetime": "2022-08-11T13:00",
                    "end_datetime": "2022-08-11T20:30"
                },
                {'message': get_text("time_out_of_schedule").format('2022-08-11T06:00:00 - 2022-08-11T16:00:00')},
                400
        ),
        # give a datetime range that is already taken
        (
                2,
                {
                    "start_datetime": "2022-08-03T14:00",
                    "end_datetime": "2022-08-03T16:00",
                    "add_tables": [1, 2, 3, 6]
                },
                {'message': get_text("order_err_busy_time").format([1, 2, 3])},
                400
        ),
        # instead of the fields 'add_tables' or 'delete_tables' give 'tables'
        (
                2,
                {'tables': [1, 2, 3]},
                {'message': get_text("err_patch_no_data")},
                400
        ),
        # give wrong table ids for add
        (
                2,
                {
                    "add_tables": [
                        4, 200, 300
                    ]
                },
                {'message': get_text("not_found").format('table', '200')},
                404
        ),
        # give wrong table ids for delete
        (
                2,
                {
                    "delete_tables": [
                        1, 200, 300
                    ]
                },
                {'message': get_text("patch").format('order', '2')},
                200
        ),
        # give wrong user_id
        pytest.param(
            2,
            {'user_id': 10},
            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about non-existent key value 'user_id' = '10'"}
            },
            400,
            marks=pytest.mark.xfail(reason="non-existent key value 'user_id' = '10'")
        ),
    ])
    def test_patch_wrong_order(self, order_id, json_to_send, result_json, status, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.patch(
                f'{api_url}/orders/{order_id}', json=json_to_send, headers=token
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
        # give end datetime which is less than start datetime
        (
                {
                    "start_datetime": "2022-08-05T10:00",
                    "end_datetime": "2022-08-05T09:00",
                    "user_id": 1,
                    "tables": [
                        1, 2, 3
                    ]
                },
                {'message': get_text("order_err_end_less_start")},
                400
        ),
        # give a different day for the end datetime than the start datetime
        (
                {
                    "start_datetime": "2022-08-05T10:00",
                    "end_datetime": "2022-08-15T09:00",
                    "user_id": 1,
                    "tables": [
                        1, 2, 3
                    ]
                },
                {'message': get_text("order_err_not_same_day")},
                400
        ),
        # give a datetime range that is inside the break time range
        (
                {
                    "start_datetime": "2022-08-15T10:00",
                    "end_datetime": "2022-08-15T14:00",
                    "user_id": 1,
                    "tables": [
                        1, 2, 3
                    ]
                },
                {'message': get_text("time_inside_break").format('2022-08-15T13:00:00 - 2022-08-15T13:59:59')},
                400
        ),
        # give a datetime range that is outside the time range of the daily schedule
        (
                {
                    "start_datetime": "2022-08-15T14:00",
                    "end_datetime": "2022-08-15T22:00",
                    "user_id": 1,
                    "tables": [
                        1, 2, 3
                    ]
                },
                {'message': get_text("time_out_of_schedule").format('2022-08-15T08:00:00 - 2022-08-15T17:00:00')},
                400
        ),
        # give a datetime range that is already taken
        (
                {
                    "start_datetime": "2022-08-03T08:30",
                    "end_datetime": "2022-08-03T09:30",
                    "user_id": 1,
                    "tables": [
                        1, 2, 3, 6
                    ]
                },
                {'message': get_text("order_err_busy_time").format([6])},
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
    def test_post_wrong_order(self, json_to_send, result_json, status, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.post(
                f'{api_url}/orders/create', json=json_to_send, headers=token
            )
            assert response.status_code == status
            assert 'application/json' in response.headers['Content-Type']
            assert response.json() == result_json


class TestOtherException:
    @pytest.mark.parametrize("json_to_send", [
        {
            "status": "confirmed",
            "add_tables": [2, 3, 4, 5],
            "delete_tables": [1, 2, 6]
        }
    ])
    def test_forbidden_request(self, json_to_send, client):
        response_delete = client.delete(
            f'{api_url}/orders/1', headers=confirmed_client_token
        )
        response_patch = client.patch(
            f'{api_url}/orders/1', json=json_to_send, headers=confirmed_client_token
        )
        responses: tuple = (response_delete, response_patch)
        for response in responses:
            assert response.status_code == 404
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('not_found').format('order', 1)

    @pytest.mark.parametrize("json_to_send_patch, json_to_send_post", [
        (
                {
                    "status": "confirmed",
                    "add_tables": [2, 3, 4, 5],
                    "delete_tables": [1, 2, 6]
                },
                {
                    "start_datetime": "2022-08-10T08:00",
                    "end_datetime": "2022-08-10T14:59",
                    "user_id": 1,
                    "tables": [
                        1,
                        2,
                        3
                    ]
                }
        )
    ])
    def test_not_confirmed_request(self, json_to_send_patch, json_to_send_post, client):
        response_get = client.get(
            f'{api_url}/orders/', headers=unconfirmed_client_token
        )
        response_get_by_id = client.get(
            f'{api_url}/orders/1', headers=unconfirmed_client_token
        )
        response_delete = client.delete(
            f'{api_url}/orders/1', headers=unconfirmed_client_token
        )
        response_patch = client.patch(
            f'{api_url}/orders/1', json=json_to_send_patch, headers=unconfirmed_client_token
        )
        response_post = client.post(
            f'{api_url}/orders/create', json=json_to_send_post, headers=unconfirmed_client_token
        )
        responses: tuple = (response_get, response_get_by_id, response_delete, response_patch, response_post)
        for response in responses:
            assert response.status_code == 401
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('email_not_confirmed')
