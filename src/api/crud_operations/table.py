from datetime import date, datetime as dt

from sqlalchemy import and_, asc

from src.api.models.table import TableModel
from src.api.models.order import OrderModel
from src.api.models.relationships import orders_tables
from src.api.schemes.table.base_schemes import TablePatchSchema
from src.api.crud_operations.base_crud_operations import ModelOperation
from src.api.crud_operations.utils.other import process_end_datetime


class TableOperation(ModelOperation):
    def __init__(self, db, user):
        self.model = TableModel
        self.model_name = 'table'
        self.patch_schema = TablePatchSchema
        self.db = db
        self.user = user

    def find_all_by_params(self, **kwargs) -> list[TableModel]:
        """
        Finds all tables in the db by given parameters.
        But before that it checks the user's access.
        :param kwargs: dictionary with parameters.
        :return: tables list or an empty list if no tables were found.
        """
        type = kwargs.get('type')
        number_of_seats = kwargs.get('number_of_seats')
        price_per_hour = kwargs.get('price_per_hour')
        start_datetime: dt | date = kwargs.get('start_datetime')
        end_datetime: dt = process_end_datetime(kwargs.get('end_datetime'))

        subquery_for_search_by_start_and_end = (
            self.db
            .query(TableModel.id)
            .outerjoin(orders_tables)
            .outerjoin(OrderModel)
            .filter(and_(
                (OrderModel.end_datetime >= start_datetime
                 if start_datetime is not None else True),
                (OrderModel.start_datetime <= end_datetime
                 if end_datetime is not None else True)
            )
            )
            .scalar_subquery()
        ) if (start_datetime and end_datetime) else None

        subquery_for_search_by_start = (
            self.db
            .query(TableModel.id)
            .outerjoin(orders_tables)
            .outerjoin(OrderModel)
            .filter(and_(
                (OrderModel.start_datetime >= start_datetime
                 if start_datetime is not None and end_datetime is None else True)
            )
            )
            .scalar_subquery()
        ) if start_datetime is not None and end_datetime is None else None

        subquery_for_search_by_end = (
            self.db
            .query(TableModel.id)
            .outerjoin(orders_tables)
            .outerjoin(OrderModel)
            .filter(and_(
                (OrderModel.end_datetime <= end_datetime
                 if end_datetime is not None and start_datetime is None else True)
            )
            )
            .scalar_subquery()
        ) if end_datetime is not None and start_datetime is None else None

        return (self.db
                .query(TableModel)
                .filter(and_(
                    (
                        TableModel.type == type
                        if type is not None else True
                    ),
                    (
                        TableModel.number_of_seats <= number_of_seats
                        if number_of_seats is not None else True
                    ),
                    (
                        TableModel.price_per_hour <= price_per_hour
                        if price_per_hour is not None else True
                    ),
                    (
                        TableModel.id.in_(subquery_for_search_by_start_and_end)
                        if (start_datetime and end_datetime) else True
                    ),
                    (
                        TableModel.id.in_(subquery_for_search_by_start)
                        if start_datetime is not None and end_datetime is None else True
                    ),
                    (
                        TableModel.id.in_(subquery_for_search_by_end)
                        if end_datetime is not None and start_datetime is None else True
                    )
                )
                )
                .order_by(asc(self.model.id))
                .all()
                )
