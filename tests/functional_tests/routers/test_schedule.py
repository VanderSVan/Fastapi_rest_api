import pytest

from src.utils.responses.main import get_text


class TestSchedule:
    # GET
    def test_get_all_schedules(self, client, superuser_token_headers):
        response = client.get(
            f'/schedules/', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']

    @pytest.mark.parametrize("schedule_id, output_day", [
        (1, 'Monday'),
        (4, 'Thursday'),
        (6, 'Saturday')
    ])
    def test_get_schedule_by_id(self, schedule_id, output_day, client, superuser_token_headers):
        response = client.get(
            f'/schedules/{schedule_id}', headers=superuser_token_headers
        )
        response_day = response.json()['day']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_day == output_day

    @pytest.mark.parametrize("day", ['Monday', 'Wednesday', 'Friday'])
    def test_get_by_day(self, day, client, superuser_token_headers):
        response = client.get(
            f'/schedules/?day={day}', headers=superuser_token_headers
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
    def test_get_by_open_time(self, open_time, number_of_schedules, client, superuser_token_headers):
        response = client.get(
            f'/schedules/?open_time={open_time}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_schedules

    @pytest.mark.parametrize("close_time, number_of_schedules", [
        ('16:00:00', 3),
        ('17:00', 5),
        ('23:00', 8)
    ])
    def test_get_by_close_time(self, close_time, number_of_schedules, client, superuser_token_headers):
        response = client.get(
            f'/schedules/?close_time={close_time}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_schedules

    @pytest.mark.parametrize("break_start_time, number_of_schedules", [
        ('12:00:00', 5),
        ('13:00', 3),
        ('14:00', 1)
    ])
    def test_get_by_break_start_time(self, break_start_time, number_of_schedules, client, superuser_token_headers):
        response = client.get(
            f'/schedules/?break_start_time={break_start_time}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_schedules

    @pytest.mark.parametrize("break_end_time, number_of_schedules", [
        ('13:00:00', 2),
        ('14:00', 4),
        ('15:00', 5)
    ])
    def test_get_by_break_end_time(self, break_end_time, number_of_schedules, client, superuser_token_headers):
        response = client.get(
            f'/schedules/?break_end_time={break_end_time}', headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert len(response.json()) == number_of_schedules

    # DELETE
    def test_delete_schedule_by_id(self, client, superuser_token_headers):
        response = client.delete(
            '/schedules/6', headers=superuser_token_headers
        )
        response_msg = response.json()['message']
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response_msg == get_text('delete').format('schedule', 6)

    # PATCH
    @pytest.mark.parametrize("schedule_id, json_to_send, result_json", [
        (
                1,
                {
                    "day": "Monday",
                    "open_time": "12:00",
                    "close_time": "20:00"
                },
                {
                    'message': get_text("patch").format('schedule', 1)
                }
        )
    ])
    def test_patch_schedule_by_id(self, schedule_id, json_to_send, result_json, client, superuser_token_headers):
        response = client.patch(
            f'/schedules/{schedule_id}', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    # POST
    @pytest.mark.parametrize("json_to_send, result_json", [
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
                }
        )
    ])
    def test_post_schedule(self, json_to_send, result_json, client, superuser_token_headers):
        response = client.post(
            '/schedules/create', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == 201
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json


class TestScheduleException:
    @pytest.mark.parametrize("schedule_id, json_to_send, result_json", [
        # don't give required fields:
        (
                1,
                {
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                {
                    'message': get_text("schedule_err_required")
                }
        ),
        # give equal fields open and close time
        (
                2,
                {
                    "day": "2023-01-01",
                    "open_time": "15:00",
                    "close_time": "15:00",
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                {
                    'message': get_text("schedule_err_open_equal_close")
                }
        ),
        # give equal fields break time
        (
                3,
                {
                    "day": "2023-01-01",
                    "open_time": "15:00",
                    "close_time": "18:00",
                    "break_start_time": "18:00",
                    "break_end_time": "18:00"
                },
                {
                    'message': get_text("schedule_err_break_equal")
                }
        ),
        # give open time that more than close time
        (
                4,
                {
                    "day": "2023-01-01",
                    "open_time": "18:00",
                    "close_time": "15:00",
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                {
                    'message': get_text("schedule_err_close_less_open")
                }
        ),
        # give break start time that more than break end time
        (
                5,
                {
                    "day": "2023-01-01",
                    "open_time": "15:00",
                    "close_time": "18:00",
                    "break_start_time": "18:00",
                    "break_end_time": "17:00"
                },
                {
                    'message': get_text("schedule_err_break_end_less_start")
                }
        ),
        # schedule already exists
        pytest.param(
            6,
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
            }
            ,
            marks=pytest.mark.xfail(reason="repeated key value 'day' = 'Tuesday'")
        ),
    ])
    def test_patch_wrong_schedule(self, schedule_id, json_to_send, result_json, client, superuser_token_headers):
        response = client.patch(
            f'/schedules/{schedule_id}', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == 400
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

    @pytest.mark.parametrize("json_to_send, result_json", [
        # don't give required fields:
        (
                {
                    "break_start_time": "18:00",
                    "break_end_time": "18:30"
                },
                {
                    'message': get_text("schedule_err_required")
                }
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
                }
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
                }
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
                }
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
                }
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
            }
            ,
            marks=pytest.mark.xfail(reason="repeated key value 'day' = 'Tuesday'")
        ),
    ])
    def test_post_wrong_schedule(self, json_to_send, result_json, client, superuser_token_headers):
        response = client.post(
            '/schedules/create', json=json_to_send, headers=superuser_token_headers
        )
        assert response.status_code == 400
        assert 'application/json' in response.headers['Content-Type']
        assert response.json() == result_json

