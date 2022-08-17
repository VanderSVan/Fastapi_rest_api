import pytest

from tests.functional_tests.conftest import (superuser_token,
                                             admin_token,
                                             confirmed_client_token,
                                             unconfirmed_client_token)
from tests.functional_tests.test_data import schedules_json

from src.utils.response_generation.main import get_text


class TestSchedule:
    # GET
    def test_get_all_schedules(self, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/schedules/', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == len(schedules_json)

    @pytest.mark.parametrize("schedule_id, output_day", [
        (1, 'Monday'),
        (4, 'Thursday'),
        (6, 'Saturday')
    ])
    def test_get_schedule_by_id(self, schedule_id, output_day, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/schedules/{schedule_id}', headers=token
            )
            response_day = response.json()['day']
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert response_day == output_day

    @pytest.mark.parametrize("day", ['Monday', 'Wednesday', 'Friday'])
    def test_get_by_day(self, day, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/schedules/?day={day}', headers=token
            )
            response_day = response.json()[0]['day']
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert response_day == day

    @pytest.mark.parametrize("open_time, number_of_schedules", [
        ('06:00:00', 8),
        ('08:00', 6),
        ('15:00', 1)
    ])
    def test_get_by_open_time(self, open_time, number_of_schedules, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/schedules/?open_time={open_time}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_schedules

    @pytest.mark.parametrize("close_time, number_of_schedules", [
        ('16:00:00', 3),
        ('17:00', 5),
        ('23:00', 8)
    ])
    def test_get_by_close_time(self, close_time, number_of_schedules, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/schedules/?close_time={close_time}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_schedules

    @pytest.mark.parametrize("break_start_time, number_of_schedules", [
        ('12:00:00', 5),
        ('13:00', 3),
        ('14:00', 1)
    ])
    def test_get_by_break_start_time(self, break_start_time, number_of_schedules, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/schedules/?break_start_time={break_start_time}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_schedules

    @pytest.mark.parametrize("break_end_time, number_of_schedules", [
        ('13:00', 2),
        ('14:00', 4),
        ('15:00', 5)
    ])
    def test_get_by_break_end_time(self, break_end_time, number_of_schedules, client):
        for token in superuser_token, admin_token, confirmed_client_token:
            response = client.get(
                f'/schedules/?break_end_time={break_end_time}', headers=token
            )
            assert response.status_code == 200
            assert 'application/json' in response.headers['Content-Type']
            assert len(response.json()) == number_of_schedules

    # DELETE
    @pytest.mark.parametrize('token', [superuser_token, admin_token])
    def test_delete_schedule_by_id(self, token, client):
        response = client.delete(
            '/schedules/6', headers=token
        )
        response_msg = response.json()['message']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_msg == get_text('delete').format('schedule', 6)

    # PATCH
    @pytest.mark.parametrize("schedule_id, json_to_send, result_json, token", [
        (
                1,
                {"close_time": "20:00"},
                {'message': get_text("patch").format('schedule', 1)},
                superuser_token
        ),
        (
                1,
                {"close_time": "20:00"},
                {'message': get_text("patch").format('schedule', 1)},
                admin_token
        )
    ])
    def test_patch_schedule_by_id(self, schedule_id, json_to_send, result_json, token, client):
        response = client.patch(
            f'/schedules/{schedule_id}', json=json_to_send, headers=token
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    # POST
    @pytest.mark.parametrize("json_to_send, result_json, token", [
        (
                {
                    "day": "2023-01-01",
                    "open_time": "15:00",
                    "close_time": "22:00",
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                {
                    'message': get_text("post").format('schedule', 9)
                },
                superuser_token
        ),
        (
                {
                    "day": "2023-01-01",
                    "open_time": "15:00",
                    "close_time": "22:00",
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                {
                    'message': get_text("post").format('schedule', 9)
                },
                admin_token
        )
    ])
    def test_post_schedule(self, json_to_send, result_json, token, client):
        response = client.post(
            '/schedules/create', json=json_to_send, headers=token
        )
        assert response.status_code == 201
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json


class TestScheduleException:
    @pytest.mark.parametrize("schedule_id, json_to_send, result_json", [
        # give equal fields open and close time
        (
                1,
                {
                    "open_time": "15:00",
                    "close_time": "15:00"
                },
                {'message': get_text("schedule_err_open_equal_close")}
        ),
        # give close time that equal open time
        (
                2,
                {"close_time": "08:00:00"},
                {'message': get_text("schedule_err_open_equal_close")}
        ),
        # give equal fields break time
        (
                3,
                {
                    "break_start_time": "18:00",
                    "break_end_time": "18:00"
                },
                {'message': get_text("schedule_err_break_equal")}
        ),
        # give break end time that equal break start time
        (
                4,
                {"break_end_time": "12:00:00"},
                {'message': get_text("schedule_err_break_equal")}
        ),
        # give open time that more than close time
        (
                5,
                {
                    "open_time": "18:00",
                    "close_time": "15:00"
                },
                {'message': get_text("schedule_err_close_less_open")}
        ),
        # give break start time that more than break end time
        (
                6,
                {
                    "break_start_time": "18:00",
                    "break_end_time": "17:00"
                },
                {'message': get_text("schedule_err_break_end_less_start")}
        ),
        # schedule already exists
        pytest.param(
            6,
            {"day": "Tuesday"},

            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about repeated key value 'day' = 'Tuesday'"}
            }
            ,
            marks=pytest.mark.xfail(reason="'day' = 'Tuesday' already exists")
        ),
    ])
    def test_patch_wrong_schedule(self, schedule_id, json_to_send, result_json, client):
        for token in superuser_token, admin_token:
            response = client.patch(
                f'/schedules/{schedule_id}', json=json_to_send, headers=token
            )
            assert response.status_code == 400
            assert 'application/json' in response.headers['Content-Type']
            assert response.json() == result_json

    @pytest.mark.parametrize("json_to_send, result_json, status", [
        # don't give required fields:
        (
                {
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                # it's pydantic output:
                {
                    'detail': [
                        {'loc': ['body', 'day'], 'msg': 'field required', 'type': 'value_error.missing'},
                        {'loc': ['body', 'open_time'], 'msg': 'field required', 'type': 'value_error.missing'},
                        {'loc': ['body', 'close_time'], 'msg': 'field required', 'type': 'value_error.missing'}
                    ]
                },
                422
        ),
        # give equal fields open and close time
        (
                {
                    "day": "2023-01-01",
                    "open_time": "15:00",
                    "close_time": "15:00",
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                {
                    'message': get_text("schedule_err_open_equal_close")
                },
                400
        ),
        # give equal fields break time
        (
                {
                    "day": "2023-01-01",
                    "open_time": "15:00",
                    "close_time": "18:00",
                    "break_start_time": "18:00",
                    "break_end_time": "18:00"
                },
                {
                    'message': get_text("schedule_err_break_equal")
                },
                400
        ),
        # give open time that more than close time
        (
                {
                    "day": "2023-01-01",
                    "open_time": "18:00",
                    "close_time": "15:00",
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                {
                    'message': get_text("schedule_err_close_less_open")
                },
                400
        ),
        # give break start time that more than break end time
        (
                {
                    "day": "2023-01-01",
                    "open_time": "15:00",
                    "close_time": "18:00",
                    "break_start_time": "18:00",
                    "break_end_time": "17:00"
                },
                {
                    'message': get_text("schedule_err_break_end_less_start")
                },
                400
        ),
        # schedule already exists
        pytest.param(
            {
                "day": "Tuesday",
                "open_time": "08:00:00",
                "close_time": "17:00:00",
                "break_start_time": "13:00:00",
                "break_end_time": "14:00:00",
            },

            {
                "message": {'err_name': 'sqlalchemy.exc.IntegrityError',
                            'traceback': "something about repeated key value 'day' = 'Tuesday'"}
            },
            400,
            marks=pytest.mark.xfail(reason="repeated key value 'day' = 'Tuesday'")
        ),
    ])
    def test_post_wrong_schedule(self, json_to_send, result_json, status, client):
        for token in superuser_token, admin_token:
            response = client.post(
                '/schedules/create', json=json_to_send, headers=token
            )
            assert response.status_code == status
            assert 'application/json' in response.headers['Content-Type']
            assert response.json() == result_json

    @pytest.mark.parametrize("patch_json_to_send, post_json_to_send", [
        (
            {"close_time": "20:00"},
            {
                "day": "2023-01-01",
                "open_time": "15:00",
                "close_time": "22:00",
                "break_start_time": "18:00",
                "break_end_time": "18:30"
            }
        )

    ])
    def test_forbidden_request(self, patch_json_to_send, post_json_to_send, client):
        response_delete = client.delete(
            '/schedules/1', headers=confirmed_client_token
        )
        response_patch = client.patch(
            '/schedules/1', json=patch_json_to_send, headers=confirmed_client_token
        )
        response_post = client.post(
            '/schedules/create', json=post_json_to_send, headers=confirmed_client_token
        )
        responses: tuple = (response_delete, response_patch, response_post)
        for response in responses:
            assert response.status_code == 403
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('forbidden_request')

    @pytest.mark.parametrize("json_to_send_patch, json_to_send_post", [
        (
                {
                    "day": "Monday",
                    "open_time": "08:00",
                    "close_time": "22:00",
                    "break_start_time": "13:00",
                    "break_end_time": "14:00"
                },
                {
                    "day": "2022-12-25",
                    "open_time": "10:00",
                    "close_time": "23:00",
                    "break_start_time": "14:00",
                    "break_end_time": "15:00"
                }
        )
    ])
    def test_not_confirmed_request(self, json_to_send_patch, json_to_send_post, client):
        response_get = client.get(
            '/schedules/', headers=unconfirmed_client_token
        )
        response_get_by_id = client.get(
            '/schedules/1', headers=unconfirmed_client_token
        )
        response_delete = client.delete(
            '/schedules/1', headers=unconfirmed_client_token
        )
        response_patch = client.patch(
            '/schedules/1', json=json_to_send_patch, headers=unconfirmed_client_token
        )
        response_post = client.post(
            '/schedules/create', json=json_to_send_post, headers=unconfirmed_client_token
        )
        responses: tuple = (response_get, response_get_by_id, response_delete, response_patch, response_post)
        for response in responses:
            assert response.status_code == 401
            assert 'application/json' in response.headers['Content-Type']
            assert response.json()['message'] == get_text('email_not_confirmed')
