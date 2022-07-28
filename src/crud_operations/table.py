from sqlalchemy import and_

from .base_crud_operations import ModelOperation
from ..models.table import TableModel
from ..schemes.table.base_schemes import TablePatchSchema


class TableOperation(ModelOperation):
    def __init__(self, db):
        self.model = TableModel
        self.patch_schema = TablePatchSchema
        self.response_elem_name = 'table'
        self.db = db

    def find_all_by_params(self, **kwargs) -> list[TableModel]:
        type = kwargs.get('type')
        number_of_seats = kwargs.get('number_of_seats')
        price_per_hour = kwargs.get('price_per_hour')
        return (self.db
                .query(TableModel)
                .filter(and_(
                             (TableModel.type == type
                              if type is not None else True),
                             (TableModel.number_of_seats <= number_of_seats
                              if number_of_seats is not None else True),
                             (TableModel.price_per_hour <= price_per_hour
                              if price_per_hour is not None else True)
                            )
                        )
                .all())
