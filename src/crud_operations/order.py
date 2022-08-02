from datetime import datetime as dt
from typing import NoReturn

from fastapi import status
from sqlalchemy import and_
from datetimerange import DateTimeRange

from src.models.order import OrderModel
from src.models.table import TableModel
from src.schemes.order.base_schemes import (OrderPatchSchema,
                                            OrderPostSchema)
from src.utils.exceptions import JSONException
from src.utils.responses.main import get_text
from src.crud_operations.base_crud_operations import ModelOperation
from src.crud_operations.table import TableOperation


class OrderOperation(ModelOperation):
    def __init__(self, db, user):
        self.model = OrderModel
        self.model_name = 'order'
        self.patch_schema = OrderPatchSchema
        self.db = db
        self.user = user

    def find_all_by_params(self, **kwargs) -> list[OrderModel] | list[None]:
        """
        Finds all orders in the db by given parameters.
        But before that it checks the user's access.
        :param kwargs: dictionary with parameters.
        :return: orders list or an empty list if no orders were found.
        """
        # Checking user access.
        if not self.check_user_access():
            user_id = self.user.id
        else:
            user_id = kwargs.get('user_id')

        start_datetime = kwargs.get('start_datetime')
        end_datetime = kwargs.get('end_datetime')
        status_ = kwargs.get('status')
        cost = kwargs.get('cost')

        return (
            self.db
                .query(OrderModel)
                .filter(and_(
                             (OrderModel.start_datetime >= start_datetime
                              if start_datetime is not None else True),
                             (OrderModel.end_datetime >= end_datetime
                              if end_datetime is not None else True),
                             (OrderModel.status == status_
                              if status_ is not None else True),
                             (OrderModel.cost <= cost
                              if cost is not None else True),
                             (OrderModel.user_id == user_id
                              if user_id is not None else True)
                             )
                        )
                .all()
        )

    def update_obj(self, id_: int, new_data: OrderPatchSchema) -> OrderModel:
        """
        Updates order values into db with new data.
        If the user does not have access rights, then the error is raised.
        :param id_: order id.
        :param new_data: new order data to update.
        :return: updated order.
        """
        # Get order object from db or raise 404 exception.
        # This is where user access is checked.
        old_order: OrderModel = self.find_by_id_or_404(id_)

        # Check free time in order list.
        if not self._check_free_time_in_orders(new_data.start_datetime, new_data.end_datetime):
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="This time is already taken"
            )

        # Get nested tables.
        existing_order_tables: list[TableModel] = old_order.tables

        # Extract order data by scheme.
        old_order_data: OrderPatchSchema = self.patch_schema(**old_order.__dict__)

        # Update order data.
        data_to_update: dict = new_data.dict(exclude_unset=True)  # remove fields where value is None
        updated_data: OrderPatchSchema = old_order_data.copy(update=data_to_update)  # replace only changed data

        # Update order.
        for key, value in updated_data:
            self._add_or_delete_order_tables(key, value, existing_order_tables)

            if hasattr(old_order, key):
                setattr(old_order, key, value)

        # Save updated order.
        updated_order: OrderModel = old_order
        self.db.commit()
        self.db.refresh(updated_order)

        return updated_order

    def add_obj(self, new_data: OrderPostSchema) -> OrderModel:
        """
        Adds new order into db if the order time is free else raises exception.
        :param new_data: new order data.
        :return: added order.
        """
        if not self._check_free_time_in_orders(new_data.start_datetime, new_data.end_datetime):
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="This time is already taken")

        max_order_id: int = self.get_max_id()
        new_order: OrderModel = self.model(id=max_order_id + 1, **new_data.dict())

        self.db.add(new_order)
        self.db.commit()
        self.db.refresh(new_order)

        return new_order

    def _add_or_delete_order_tables(self,
                                    action: str,
                                    new_table_ids: list[int],
                                    existing_tables: list[TableModel]
                                    ) -> NoReturn:
        """
        Adds or deletes tables from order.
        :param action: table action - delete or add.
        :param new_table_ids: new table numbers.
        :param existing_tables: existing table objects.
        """
        if action == 'tables':
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=get_text('err_patch').format('add_tables', 'delete_tables', 'tables')
            )
        if action == 'add_tables' and new_table_ids:
            new_tables: list[TableModel] = self._collect_new_tables(new_table_ids, existing_tables)
            existing_tables.extend(new_tables)

        elif action == 'delete_tables' and new_table_ids:
            for table_number, table in enumerate(existing_tables):
                if table.id in new_table_ids:
                    del existing_tables[table_number]

    def _check_free_time_in_orders(self, start: dt, end: dt) -> bool:
        """Returns True if time is free else False"""
        input_time_range = DateTimeRange(start, end)
        orders_for_day: list[OrderModel] = self.find_all_by_params(start_datetime=start.date())
        occupied_orders: list[OrderModel] = [
            order
            for order in orders_for_day
            if (DateTimeRange(order.start_datetime, order.end_datetime) in input_time_range)
               or
               (str(start) in DateTimeRange(order.start_datetime, order.end_datetime))
               or
               (str(end) in DateTimeRange(order.start_datetime, order.end_datetime))
        ]
        return False if occupied_orders else True

    def _collect_new_tables(self,
                            new_table_ids: list[int],
                            existing_tables: list[TableModel]
                            ) -> list[TableModel]:
        """Creates a list with new tables excluding existing ones."""
        table_operation = TableOperation(self.db)
        existing_table_ids: list[int] = [table_obj.id for table_obj in existing_tables]
        return [table_operation.find_by_id_or_404(table_id)
                for table_id in new_table_ids
                if table_id not in existing_table_ids]
