from typing import NoReturn
from datetime import date

from fastapi import status
from sqlalchemy import and_

from src.models.order import OrderModel
from src.models.table import TableModel
from src.schemes.order.base_schemes import (OrderPatchSchema,
                                            OrderPostSchema)
from src.crud_operations.base_crud_operations import ModelOperation
from src.crud_operations.schedule import ScheduleOperation
from src.crud_operations.table import TableOperation
from src.crud_operations.utils import OrderUtils
from src.utils.exceptions import JSONException


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
        # Check input data
        self._check_input_data(new_data)

        # Get order object from db or raise 404 exception.
        # This is where user access is checked.
        old_order: OrderModel = self.find_by_id_or_404(id_)

        # Get nested tables.
        existing_order_tables: list[TableModel] = old_order.tables

        # Extract order data by scheme.
        old_order_data: OrderPatchSchema = self.patch_schema(**old_order.__dict__)

        # Update order data.
        data_to_update: dict = new_data.dict(exclude_unset=True)  # remove fields where value is None
        updated_data: OrderPatchSchema = old_order_data.copy(update=data_to_update)  # replace only changed data

        # Update order.
        for key, value in updated_data:
            OrderUtils.add_or_delete_order_tables(key, value, existing_order_tables, self.db)

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
        # Check input data
        self._check_input_data(new_data)

        prepared_data: dict = self._prepare_data_for_post_operation(new_data)
        max_order_id: int = self.get_max_id()
        new_order: OrderModel = self.model(id=max_order_id + 1, **prepared_data)

        self.db.add(new_order)
        self.db.commit()
        self.db.refresh(new_order)

        return new_order

    def _check_input_data(self, data: OrderPostSchema | OrderPatchSchema) -> NoReturn:
        """
        Checks data for all parameters.
        :param data: input data.
        :raises: JSONException.
        """
        # Additional variables
        schedule_operation: ScheduleOperation = ScheduleOperation(db=self.db, user=None)

        if data.start_datetime and data.end_datetime:
            # Check that the time range is on the schedule
            OrderUtils.check_time_range_within_schedule_range(
                data.start_datetime,
                data.end_datetime,
                schedule_operation
            )
            # Check that time is not busy in other orders
            date_: date = data.start_datetime.date()
            orders_for_day: list[OrderModel] = self.find_all_by_params(start_datetime=date_)
            if not OrderUtils.check_free_time_in_orders(
                    orders_for_day,
                    data.start_datetime,
                    data.end_datetime
            ):
                raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                    message="This time is already taken")

    def _prepare_data_for_post_operation(self, data: OrderPostSchema) -> dict:
        """
        Converts table ids to table objects.
        Calculates order cost.
        :param data: input data.
        :return: prepared data as dict.
        """
        table_operation: TableOperation = TableOperation(db=self.db, user=None)

        if data.tables:
            data.tables = OrderUtils.convert_ids_to_table_objs(data.tables, table_operation)

        checked_data: dict = data.dict()
        checked_data['cost'] = OrderUtils.calculate_cost(data.start_datetime,
                                                         data.end_datetime,
                                                         data.tables)
        return checked_data
