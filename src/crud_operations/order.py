from datetime import datetime as dt
from datetime import timedelta as td
from math import ceil

from fastapi import status
from pydantic import BaseModel as BaseSchema
from sqlalchemy import and_
from datetimerange import DateTimeRange

from ..db.db_sqlalchemy import SessionLocal
from ..models.order import OrderModel
from ..models.table import TableModel
from ..schemas.order.base_schemas import OrderPatchSchema, OrderPostSchema
from ..utils.exceptions import JSONException
from ..utils.responses.main import get_text
from .base_crud_operations import ModelOperation
from .table import TableOperation


class OrderOperation(ModelOperation):
    def __init__(self, db):
        self.model = OrderModel
        self.patch_schema = OrderPatchSchema
        self.response_elem_name = 'order'
        self.db = db

    def find_all_by_params(self, **kwargs) -> list[OrderModel]:
        start_datetime = kwargs.get('start_datetime')
        end_datetime = kwargs.get('end_datetime')
        status_ = kwargs.get('status')
        cost = kwargs.get('cost')
        client_id = kwargs.get('client_id')
        return (self.db
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
                             (OrderModel.client_id == client_id
                              if client_id is not None else True)
                        )
                        )
                .all())

    def update_model(self, id_: int, new_data: OrderPatchSchema) -> OrderModel:
        # get order model from db or raise 404 exception
        old_model_without_tables: OrderModel = self.find_by_id_or_404(id_)

        if not self._check_free_time_in_orders(new_data.start_datetime, new_data.end_datetime):
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="This time is already taken")

        # get nested tables
        existing_tables: list[TableModel] = old_model_without_tables.tables
        existing_table_ids: list[int] = [table_obj.id for table_obj in existing_tables]

        # transform order model to order schema
        old_data_without_tables: BaseSchema = self.patch_schema(**old_model_without_tables.__dict__)

        # update order schema by new_data
        data_to_update: dict = new_data.dict(exclude_unset=True)
        updated_data: BaseSchema = old_data_without_tables.copy(update=data_to_update)

        # update order model
        for key, value in updated_data:
            if key == 'tables':
                raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                    message=get_text('err_patch').format('add_tables', 'delete_tables', 'tables'))

            if key == 'add_tables' and value:
                new_tables: list[TableModel] = self._collect_new_tables(value, existing_table_ids)
                existing_tables.extend(new_tables)

            elif key == 'delete_tables' and value:
                for table_number, table in enumerate(existing_tables):
                    if table.id in value:
                        del existing_tables[table_number]

            if hasattr(old_model_without_tables, key):
                setattr(old_model_without_tables, key, value)

        # save updated model
        updated_model: OrderModel = old_model_without_tables
        self.db.commit()
        self.db.refresh(updated_model)
        return updated_model

    def add_model(self, new_data: OrderPostSchema) -> OrderModel:

        if not self._check_free_time_in_orders(new_data.start_datetime, new_data.end_datetime):
            raise JSONException(status_code=status.HTTP_400_BAD_REQUEST,
                                message="This time is already taken")

        max_model_id: int = self.get_max_model_id()
        new_model = self.model(id=max_model_id + 1, **new_data.dict())
        self.db.add(new_model)
        self.db.commit()
        self.db.refresh(new_model)
        return new_model

    @staticmethod
    def _collect_new_tables(tables: list[TableModel], existing_table_ids: list[int]) -> list[TableModel]:
        db = SessionLocal()
        try:
            table_operation = TableOperation(db)
            return [table_operation.find_by_id_or_404(table_id)
                    for table_id in tables
                    if table_id not in existing_table_ids]
        finally:
            db.close()

    def _check_free_time_in_orders(self, start: dt, end: dt) -> bool:
        """Returns True if time is free else False"""

        input_time_range = DateTimeRange(start, end)
        orders_for_day: list[OrderModel] = self.find_all_by_params(start_datetime=start.date())
        occupied_orders: list[OrderModel] = [
            order
            for order in orders_for_day
            if DateTimeRange(order.start_datetime, order.end_datetime) in input_time_range
            or str(start) in DateTimeRange(order.start_datetime, order.end_datetime)
            or str(end) in DateTimeRange(order.start_datetime, order.end_datetime)
        ]
        return False if occupied_orders else True
