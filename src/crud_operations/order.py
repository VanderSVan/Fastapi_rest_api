from typing import NoReturn
from datetime import date, datetime as dt

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
from src.schemes.validators.order import OrderPostOrPatchValidator
from src.utils.exceptions import JSONException
from src.utils.responses.main import get_text


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
        If it's not superuser, it only looks for orders associated with the user id.
        :param kwargs: dictionary with parameters.
        :return: orders list or an empty list if no orders were found.
        """
        user_id: int = self.user.id if not self.check_user_access() else kwargs.get('user_id')
        start_datetime: dt | date = kwargs.get('start_datetime')
        end_datetime: dt = self._process_end_datetime(kwargs.get('end_datetime'))
        status_: str = kwargs.get('status')
        cost: float = kwargs.get('cost')

        return (
            self.db
                .query(OrderModel)
                .filter(and_(
                             (OrderModel.start_datetime >= start_datetime
                              if start_datetime is not None else True),
                             (OrderModel.end_datetime <= end_datetime
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
        # Check input data.
        self._check_input_data(new_data)

        # Get order object from db or raise 404 exception.
        # This is where user access is checked.
        old_order: OrderModel = self.find_by_id_or_404(id_)

        # Get nested tables.
        old_order_tables: list[TableModel] = old_order.tables

        # Prepare new data.
        prepared_new_data: OrderPatchSchema = self._prepare_data_for_patch_operation(old_order, new_data)

        # Update old order object.
        for key, value in prepared_new_data:
            OrderUtils.add_or_delete_order_tables(key, value, old_order_tables, self.db)
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
                                    message=get_text('order_err_busy_time'))

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

    def _prepare_data_for_patch_operation(self,
                                          old_data: OrderModel,
                                          new_data: OrderPatchSchema
                                          ) -> OrderPatchSchema:
        """
        Executes all necessary checks to update the order data.
        :param old_data: data from db.
        :param new_data: order update data.
        :return: updated data.
        """
        # Extract order data by scheme.
        old_order_data: OrderPatchSchema = self.patch_schema(**old_data.__dict__)

        # Update order data.
        data_to_update: dict = new_data.dict(exclude_unset=True)  # remove fields where value is None
        if data_to_update:
            updated_data: OrderPatchSchema = old_order_data.copy(update=data_to_update)  # replace only changed data
        else:
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=get_text('err_patch_no_data')
            )

        # Check datetime values, required if only one datetime field was given.
        OrderPostOrPatchValidator.check_datetime_values(
            updated_data.start_datetime, updated_data.end_datetime
        )

        return updated_data

    @staticmethod
    def _process_end_datetime(end: dt):
        """
        If date:
            Replaces empty time values to '23:59:59'.
            For proper search operation.
        else:
            Do nothing.
        :param end: date or datetime value.
        :return: datetime obj.
        """
        return (
            dt(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59)
            if type(end) is date else end
        )
