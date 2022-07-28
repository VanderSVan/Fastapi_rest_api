from dataclasses import dataclass
from typing import Any, NoReturn

from fastapi import status
from pydantic import BaseModel as BaseSchema
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db.db_sqlalchemy import BaseModel
from ..utils.exceptions import JSONException
from ..utils.responses.main import get_text


@dataclass
class ModelOperation:
    model: BaseModel
    patch_schema: type(BaseSchema)
    response_elem_name: str
    db: Session

    def get_max_id(self) -> int:
        query, = self.db.query(self.model).with_entities(func.max(self.model.id)).first()

        if not query:
            query = 0

        return query

    def find_all(self) -> BaseModel:
        return self.db.query(self.model).all()

    def find_by_id(self, id_: int) -> BaseModel:
        return self.db.query(self.model).filter(self.model.id == id_).first()

    def find_by_id_or_404(self, id_: int) -> BaseModel:
        query_result: BaseModel = (self.db.query(self.model).filter(self.model.id == id_).first())

        if not query_result:
            self._raise_id_not_found(id_)

        return query_result

    def find_by_param(self, param_name: str, param_value: Any) -> BaseModel:
        self._check_param(param_name)

        return (
            self.db
                .query(self.model)
                .filter(self.model.__getattribute__(param_name) == param_value)
                .first()
        )

    def find_by_param_or_404(self, param_name: str, param_value: Any) -> BaseModel:
        self._check_param(param_name)
        query_result = (
            self.db
                .query(self.model)
                .filter(self.model.__getattribute__(self.model, param_name) == param_value)
                .first()
        )

        if not query_result:
            self._raise_param_not_found(param_name, param_value)

        return query_result

    def update_model(self, id_: int, new_schema: BaseSchema) -> BaseModel:
        # Get data from db or raise 404 exception.
        old_model: BaseModel = self.find_by_id_or_404(id_)

        # Transform db model to schema.
        old_data: BaseSchema = self.patch_schema(**old_model.__dict__)

        # Update schema.
        data_to_update: dict = new_schema.dict(exclude_unset=True)  # remove fields where value is None
        updated_data: BaseSchema = old_data.copy(update=data_to_update)  # replace only changed data

        # Update db model.
        for key, value in updated_data:
            if hasattr(old_model, key):
                setattr(old_model, key, value)
        updated_model: BaseModel = old_model

        # Save new model data.
        self.db.commit()
        self.db.refresh(updated_model)
        return updated_model

    def delete_model(self, id_: int) -> NoReturn:
        model_to_delete = self.find_by_id_or_404(id_)
        self.db.delete(model_to_delete)
        self.db.commit()

    def add_model(self, new_schema: BaseSchema) -> BaseModel:
        max_model_id: int = self.get_max_id()
        new_model = self.model(id=max_model_id + 1, **new_schema.dict())
        self.db.add(new_model)
        self.db.commit()
        self.db.refresh(new_model)
        return new_model

    def _check_param(self, param_name) -> NoReturn:
        if not hasattr(self.model, param_name):
            raise JSONException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=get_text('err_500')
            )

    def _raise_id_not_found(self, id_) -> NoReturn:
        raise JSONException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=get_text('not_found').format(self.response_elem_name, id_)
        )

    def _raise_param_not_found(self, param_name, param_value) -> NoReturn:
        raise JSONException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=get_text('param_not_found').format(self.response_elem_name,
                                                       param_name,
                                                       param_value)
        )
