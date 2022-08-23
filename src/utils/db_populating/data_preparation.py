from src.api.models.user import UserModel
from src.api.models.table import TableModel
from src.api.models.schedule import ScheduleModel
from src.api.models.order import OrderModel
from src.utils.auth_utils.password_cryptograph import PasswordCryptographer


def prepare_data_for_insertion(users: list, tables: list, schedules: list, orders: list) -> dict:
    """Main function."""
    users: list[dict] = encode_user_passwords(users)

    user_models: list = [UserModel(**user_json) for user_json in users]
    table_models: list = [TableModel(**table_json) for table_json in tables]
    schedule_models: list = [ScheduleModel(**schedule_json) for schedule_json in schedules]

    prepared_order_json: list = convert_ids_to_table_objs_for_orders(orders, table_models)
    order_models: list = [OrderModel(**order_json) for order_json in prepared_order_json]

    return {'users': user_models,
            'tables': table_models,
            'schedules': schedule_models,
            'orders': order_models}


def encode_user_passwords(users: list[dict]):
    for user in users:
        user_password = user.get('password')

        if user_password:
            hashed_password = PasswordCryptographer.bcrypt(user_password)
            user['hashed_password'] = hashed_password
            del user['password']
        else:
            raise ValueError('user_json should have password field')

    return users


def find_objs_by_ids(id_list: list[int], obj_list: list) -> list:
    return [obj for obj in obj_list if obj.id in id_list]


def convert_ids_to_table_objs_for_orders(orders: list, tables: list[TableModel]) -> list[dict]:
    for order in orders:
        table_ids: list[int] = order.get('tables')
        if table_ids:
            order['tables'] = find_objs_by_ids(table_ids, tables)
    return orders
