from sqlalchemy import and_

from .base_crud_operations import ModelOperation
from ..models.client import ClientModel


class ClientOperation(ModelOperation):

    def find_all_by_params(self, **kwargs) -> list[ClientModel]:
        phone = kwargs.get('phone')
        return (self.db
                    .query(ClientModel)
                    .filter(and_(
                                 (ClientModel.phone == phone
                                  if phone is not None else True),
                                )
                            )
                    .all())
