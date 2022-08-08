from src.factory_app import create_app
from src.utils.populating_db.input_data import (users_json,
                                                tables_json,
                                                schedules_json,
                                                order_json)


app = create_app(with_data=(users_json, tables_json, schedules_json, order_json))
