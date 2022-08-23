from typing import NoReturn
from datetime import date, datetime as dt

from sqlalchemy.orm import Session
from fastapi import status

from src.api.models.table import TableModel
from src.api.schemes.validators.order import OrderPostOrPatchValidator
from src.api.crud_operations.utils.table import (collect_new_tables_excluding_existing_ones,
                                                 get_table_ids_by_booking_time)
from src.api.crud_operations.utils.schedule import check_time_range_within_schedule_range
from src.api.crud_operations.utils.other import round_timedelta_to_hours
from src.utils.exceptions import JSONException
from src.utils.response_generation.main import get_text


def add_or_delete_order_tables(action: str,
                               new_table_ids: list[int],
                               existing_tables: list[TableModel],
                               db: Session
                               ) -> NoReturn:
    """
    Adds or deletes tables from order.
    If the tables that is given for method 'add_tables' does not exist then raises exception.
    If the tables that is given for method 'delete_tables' does not exist then nothing happens.
    :param action: table action - delete or add.
    :param new_table_ids: new table numbers.
    :param existing_tables: existing table objects.
    :param db: db session.
    """
    if action == 'tables':
        raise JSONException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=get_text('err_patch').format('add_tables', 'delete_tables', 'tables')
        )
    if action == 'add_tables' and new_table_ids:
        # If the table exists, add it or raise exception if the table does not exist.
        new_tables: list[TableModel] = collect_new_tables_excluding_existing_ones(new_table_ids,
                                                                                  existing_tables,
                                                                                  db)
        existing_tables.extend(new_tables)

    elif action == 'delete_tables' and new_table_ids:
        # If the table exists, delete it or do nothing.
        for table_number, table in enumerate(existing_tables):
            if table.id in new_table_ids:
                del existing_tables[table_number]


def calculate_cost(start: dt, end: dt, tables: list[TableModel]) -> float:
    """
    Calculates order cost by table.price_per_hour
    Any timedelta is rounded to the hour.
    """
    hours: int = round_timedelta_to_hours(start, end)
    table_prices_per_hour: list = [table.price_per_hour for table in tables]
    total_price: float = sum(table_prices_per_hour)
    return hours * total_price


def validate_booking_time(start: dt | date,
                          end: dt | date,
                          new_booking_tables: list[int],
                          db: Session) -> NoReturn:
    """Validates datetime range."""
    # Check datetime values, required if only one datetime field was given.
    OrderPostOrPatchValidator.check_datetime_values(start, end)
    # Other checks.
    check_time_range_within_schedule_range(start, end, db)
    check_free_time_in_orders(start, end, new_booking_tables, db)


def check_free_time_in_orders(start: dt | date,
                              end: dt | date,
                              new_booking_tables: list[int],
                              db: Session
                              ) -> NoReturn:
    """Checks that time is not busy in other orders."""
    if new_booking_tables:
        tables_at_given_time: list[int] = get_table_ids_by_booking_time(start, end, db)

        if tables_at_given_time:
            occupied_tables: list[int] = [table for table in tables_at_given_time if table in new_booking_tables]

            if occupied_tables:
                raise JSONException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=get_text('order_err_busy_time').format(occupied_tables)
                )
