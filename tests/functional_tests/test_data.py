# !!!!!!!!! DON'T CHANGE THESE DATA !!!!!!!!!

users_json: list = [
    {
        "username": "superuser",
        "email": "superuser@example.com",
        "phone": "123456789",
        "role": "superuser",
        "id": 1,
        "status": "confirmed",
        "password": "12345678"
    },
    {
        "username": "admin",
        "email": "admin@example.com",
        "phone": "0123456789",
        "role": "admin",
        "id": 2,
        "status": "confirmed",
        "password": "123456789"
    },
    {
        "username": "client1",
        "email": "client1@example.com",
        "phone": "147852369",
        "role": "client",
        "id": 3,
        "status": "confirmed",
        "password": "123654789"
    },
    {
        "username": "client2",
        "email": "client2@example.com",
        "phone": "1478523690",
        "role": "client",
        "id": 4,
        "status": "confirmed",
        "password": "123654789"
    }
]
schedules_json: list = [
    {
        "day": "Monday",
        "open_time": "08:00:00",
        "close_time": "17:00:00",
        "break_start_time": "13:00:00",
        "break_end_time": "14:00:00",
        "id": 1
    },
    {
        "day": "Tuesday",
        "open_time": "08:00:00",
        "close_time": "17:00:00",
        "break_start_time": "13:00:00",
        "break_end_time": "14:00:00",
        "id": 2
    },
    {
        "day": "Wednesday",
        "open_time": "08:00:00",
        "close_time": "16:00:00",
        "break_start_time": None,
        "break_end_time": None,
        "id": 3
    },
    {
        "day": "Thursday",
        "open_time": "06:00:00",
        "close_time": "16:00:00",
        "break_start_time": "12:00:00",
        "break_end_time": "13:00:00",
        "id": 4
    },
    {
        "day": "Friday",
        "open_time": "06:00:00",
        "close_time": "16:00:00",
        "break_start_time": "12:00:00",
        "break_end_time": "13:00:00",
        "id": 5
    },
    {
        "day": "Saturday",
        "open_time": "10:00",
        "close_time": "23:00",
        "break_start_time": "14:00",
        "break_end_time": "15:00",
        "id": 6
    },
    {
        "day": "Sunday",
        "open_time": "10:00",
        "close_time": "22:00",
        "break_start_time": None,
        "break_end_time": None,
        "id": 7
    },
    {
        "day": "2022-03-08",
        "open_time": "15:00",
        "close_time": "23:00",
        "break_start_time": None,
        "break_end_time": None,
        "id": 8
    }
]
tables_json: list = [
    {
        "type": "standard",
        "number_of_seats": 6,
        "price_per_hour": 1500,
        "id": 1
    },
    {
        "type": "standard",
        "number_of_seats": 12,
        "price_per_hour": 2500,
        "id": 2
    },
    {
        "type": "private",
        "number_of_seats": 2,
        "price_per_hour": 3000,
        "id": 3
    },
    {
        "type": "private",
        "number_of_seats": 3,
        "price_per_hour": 4000,
        "id": 4
    },
    {
        "type": "vip_room",
        "number_of_seats": 6,
        "price_per_hour": 7000,
        "id": 5
    },
    {
        "type": "vip_room",
        "number_of_seats": 15,
        "price_per_hour": 15000,
        "id": 6
    }
]
order_json: list = [
    {
        "start_datetime": "2022-08-03T08:00",
        "end_datetime": "2022-08-03T09:59",
        "status": "processing",
        "user_id": 2,
        "tables": [
            6
        ],
        "cost": 15000
    },
    {
        "start_datetime": "2022-08-03T15:00",
        "end_datetime": "2022-08-03T15:59",
        "status": "confirmed",
        "user_id": 3,
        "tables": [
            1, 2, 3
        ],
        "cost": 7000
    },
    {
        "start_datetime": "2022-03-08T15:00",
        "end_datetime": "2022-03-08T15:59",
        "status": "confirmed",
        "user_id": 4,
        "tables": [
            4, 5, 6
        ],
        "cost": 26000
    }
]
