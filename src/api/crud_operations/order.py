from datetime import date, datetime as dt

from fastapi import status
from sqlalchemy import and_, asc, or_

from src.api.models.order import OrderModel
from src.api.models.table import TableModel
from src.api.models.relationships import orders_tables
from src.api.schemes.order.base_schemes import (OrderPatchSchema,
                                                OrderPostSchema)
from src.api.crud_operations.base_crud_operations import ModelOperation
from src.api.crud_operations.utils.order import (add_or_delete_order_tables,
                                                 calculate_cost,
                                                 validate_booking_time)
from src.api.crud_operations.utils.other import process_end_datetime
from src.api.crud_operations.utils.table import (convert_ids_to_table_objs)
from src.utils.exceptions import JSONException
from src.utils.response_generation.main import get_text


class OrderOperation(ModelOperation):
    def __init__(self, db, user):
        self.model = OrderModel
        self.model_name = 'order'
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
        end_datetime: dt = process_end_datetime(kwargs.get('end_datetime'))
        status_: str = kwargs.get('status')
        cost: float = kwargs.get('cost')
        table_ids: list[int] = kwargs.get('tables')

        subquery = (
            self.db
            .query(OrderModel.id)
            .outerjoin(orders_tables)
            .outerjoin(TableModel)
            .filter(or_(TableModel.id.in_(table_ids)))
            .scalar_subquery()
        ) if table_ids else None

        return (
            self.db
            .query(OrderModel)
            .filter(and_(
                         (OrderModel.end_datetime >= start_datetime
                          if start_datetime is not None else True),
                         (OrderModel.start_datetime <= end_datetime
                          if end_datetime is not None else True),
                         (OrderModel.status == status_
                          if status_ is not None else True),
                         (OrderModel.cost <= cost
                          if cost is not None else True),
                         (OrderModel.user_id == user_id
                          if user_id is not None else True),
                         (OrderModel.id.in_(subquery)
                          if table_ids is not None else True)
                         )
                    )
            .order_by(asc(self.model.id))
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

        # Get nested tables.
        old_order_tables: list[TableModel] = old_order.tables

        # Prepare new data.
        prepared_new_data: OrderPatchSchema = self._prepare_data_for_patch_operation(old_order,
                                                                                     new_data)
        # Update old order object.
        for key, value in prepared_new_data:
            add_or_delete_order_tables(key, value, old_order_tables, self.db)
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
        prepared_data: dict = self._prepare_data_for_post_operation(new_data)
        max_order_id: int = self.get_max_id()
        new_order: OrderModel = self.model(id=max_order_id + 1, **prepared_data)

        self.db.add(new_order)
        self.db.commit()
        self.db.refresh(new_order)

        return new_order

    def _prepare_data_for_post_operation(self, data: OrderPostSchema) -> dict:
        """
        Converts table ids to table objects.
        Calculates order cost.
        :param data: input data.
        :return: prepared data as dict.
        """
        validate_booking_time(data.start_datetime,
                              data.end_datetime,
                              data.tables,
                              self.db)
        data.tables = convert_ids_to_table_objs(data.tables, self.db)
        prepared_data: dict = data.dict()
        prepared_data['cost'] = calculate_cost(data.start_datetime,
                                               data.end_datetime,
                                               data.tables)
        return prepared_data

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
        old_order_data: OrderPatchSchema = OrderPatchSchema(**old_data.__dict__)

        # Update order data.
        # Remove fields where value is None.
        # And checks user access. If 'client' then exclude some fields.
        data_to_update: dict = (
            new_data.dict(exclude_unset=True) if self.check_user_access()
            else new_data.dict(exclude_unset=True, exclude={'status', 'user_id', 'cost'})
        )
        if data_to_update:
            # Replace only changed data
            updated_data: OrderPatchSchema = old_order_data.copy(update=data_to_update)
        else:
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=get_text('err_patch_no_data')
            )
        validate_booking_time(updated_data.start_datetime,
                              updated_data.end_datetime,
                              updated_data.add_tables,
                              self.db)
        return updated_data
