from dataclasses import dataclass
from typing import NoReturn

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
    response_elem_name: str
    db: Session

    def find_all(self) -> BaseModel:
        return self.db.query(self.model).all()

    def find_by_id(self, id_: int) -> BaseModel:
        return self.db.query(self.model).filter(self.model.id == id_).first()

    def find_by_id_or_404(self, id_: int) -> BaseModel:
        query_result: BaseModel = (self.db.query(self.model).filter(self.model.id == id_).first())
        if not query_result:
            raise JSONException(status_code=status.HTTP_404_NOT_FOUND,
                                message=get_text('not_found').format(self.response_elem_name, id_))
        return query_result

    def get_max_model_id(self) -> int:
        query, = self.db.query(self.model).with_entities(func.max(self.model.id)).first()
        if not query:
            query = 0
        return query

    def update_model(self,
                     id_: int,
                     new_schema: BaseSchema,
                     ) -> BaseModel:

        old_model: BaseModel = self.find_by_id_or_404(id_)
        for key, value in new_schema:
            if hasattr(old_model, key):
                setattr(old_model, key, value)
        updated_model = old_model
        self.db.commit()
        self.db.refresh(updated_model)
        return updated_model

    def delete_model(self, id_: int) -> NoReturn:

        model_to_delete = self.find_by_id_or_404(id_)
        self.db.delete(model_to_delete)
        self.db.commit()

    def add_model(self, schema: BaseSchema) -> BaseModel:
        max_model_id: int = self.get_max_model_id()
        new_model = self.model(id=max_model_id + 1, **schema.dict())
        self.db.add(new_model)
        self.db.commit()
        self.db.refresh(new_model)
        return new_model
