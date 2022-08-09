from sqlalchemy import and_

from src.api.models.table import TableModel
from src.api.schemes.table.base_schemes import TablePatchSchema
from src.api.crud_operations.base_crud_operations import ModelOperation


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
                .all()
                )
