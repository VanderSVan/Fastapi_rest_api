from sqlalchemy import and_

from .base_crud_operations import ModelOperation
from ..models.order import OrderModel


class OrderOperation(ModelOperation):
    def __init__(self, db):
        self.model = OrderModel
        self.response_elem_name = 'order'
        self.db = db

    def find_all_by_params(self, **kwargs) -> list[OrderModel]:
        start_datetime = kwargs.get('start_datetime')
        end_datetime = kwargs.get('end_datetime')
        is_approved = kwargs.get('is_approved')
        cost = kwargs.get('cost')
        client_id = kwargs.get('client_id')
        return (self.db
                    .query(OrderModel)
                    .filter(and_(
                                 (OrderModel.start_datetime == start_datetime
                                  if start_datetime is not None else True),
                                 (OrderModel.end_datetime >= end_datetime
                                  if end_datetime is not None else True),
                                 (OrderModel.is_approved <= is_approved
                                  if is_approved is not None else True),
                                 (OrderModel.cost <= cost
                                  if cost is not None else True),
                                 (OrderModel.client_id <= client_id
                                  if client_id is not None else True)
                                )
                            )
                    .all())
