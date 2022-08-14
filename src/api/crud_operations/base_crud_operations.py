from dataclasses import dataclass
from typing import Any, NoReturn

from fastapi import status
from pydantic import BaseModel as BaseSchema
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.db.db_sqlalchemy import BaseModel
from src.api.models.user import UserModel
from src.utils.exceptions import JSONException
from src.utils.response_generation.main import get_text


@dataclass
class ModelOperation:
    model: BaseModel
    model_name: str
    patch_schema: type(BaseSchema)
    db: Session
    user: UserModel | None = None

    def get_max_id(self) -> int:
        """
        Gets the max object id for this model in the db.
        :return: max id as int.
        """
        query, = self.db.query(self.model).with_entities(func.max(self.model.id)).first()

        if not query:
            query = 0

        return query

    def find_all(self) -> list[BaseModel]:
        """
        Finds all objects in the db.
        But before that it checks the user's access.
        If it's not superuser, it only looks for data associated with the user id.
        :return: objects list or an empty list if no objects were found.
        """
        # Checking user access
        if not self.check_user_access():
            found_objs: list[BaseModel] = (self
                                           .db
                                           .query(self.model)
                                           .filter(self.model.user_id == self.user.id)
                                           .all()
                                           )
        else:
            found_objs: list[BaseModel] = self.db.query(self.model).all()

        return found_objs

    def find_by_id(self, id_: int) -> BaseModel | None:
        """
        Finds the object by the given id.
        But before that it checks the user's access.
        If it's not superuser, it only looks for data associated with the user id.
        :param id_: object id.
        :return: object or None if object not found.
        """
        if not self.check_user_access():
            found_obj: BaseModel = (self
                                    .db
                                    .query(self.model)
                                    .filter(and_(
                                                 self.model.id == id_,
                                                 self.model.user_id == self.user.id
                                                 )
                                            )
                                    .first()
                                    )
        else:
            found_obj: BaseModel = (self
                                    .db
                                    .query(self.model)
                                    .filter(self.model.id == id_)
                                    .first()
                                    )
        return found_obj

    def find_by_id_or_404(self, id_: int) -> BaseModel:
        """
        Finds the object by the given id,
        but if there is no such object, it raises an error.
        But before that it checks the user's access.
        If it's not superuser, it only looks for data associated with the user id.
        :param id_: object id.
        :return: object or raises an error if object is not found.
        """
        # This is where user access is checked.
        found_obj: BaseModel = self.find_by_id(id_)

        if not found_obj:
            self._raise_obj_not_found(id_)

        return found_obj

    def find_by_param(self, param_name: str, param_value: Any) -> BaseModel | None:
        """
        Finds the object by the given parameter.
        But before that it checks the user's access.
        If it's not superuser, it only looks for data associated with the user id.
        :return: object or None if object not found.
        """
        self._check_param_name_in_model(param_name)

        # Checking user access
        if not self.check_user_access():
            found_obj: BaseModel = (self
                                    .db
                                    .query(self.model)
                                    .filter(and_(
                                                 getattr(self.model, param_name) == param_value,
                                                 self.model.user_id == self.user.id
                                                 )
                                            )
                                    .first()
                                    )
        else:
            found_obj: BaseModel = (self
                                    .db
                                    .query(self.model)
                                    .filter(getattr(self.model, param_name) == param_value)
                                    .first()
                                    )
        return found_obj

    def find_by_param_or_404(self, param_name: str, param_value: Any) -> BaseModel:
        """
        Finds the object by the given parameter,
        but if there is no such object, it raises an error.
        But before that it checks the user's access.
        If it's not superuser, it only looks for data associated with the user id.
        :return:
        """
        # This is where user access is checked.
        found_obj: BaseModel = self.find_by_param(param_name, param_value)

        if not found_obj:
            self._raise_param_not_found(param_name, param_value)

        return found_obj

    def update_obj(self, id_: int, new_data: BaseSchema) -> BaseModel:
        """
        Updates object values into db with new data.
        If the user does not have access rights, then the error is raised.
        :param id_: object id.
        :param new_data: new data to update.
        :return: updated object.
        """
        # Get object from db or raise 404 exception.
        # This is where user access is checked.
        old_obj: BaseModel = self.find_by_id_or_404(id_)

        # Prepare new data.
        prepared_new_data: BaseSchema = self._prepare_data_for_update_operation(old_obj, new_data)

        # Update db object.
        for key, value in prepared_new_data:
            if hasattr(old_obj, key):
                setattr(old_obj, key, value)
        updated_obj: BaseModel = old_obj

        # Save new object data into db.
        self.db.commit()
        self.db.refresh(updated_obj)

        return updated_obj

    def delete_obj(self, id_: int) -> NoReturn:
        """
        Deletes object from db by the given id object.
        If the user does not have access rights, then the error is raised.
        :param id_: object id.
        """
        # Get object from db or raise 404 exception.
        # This is where user access is checked.
        model_to_delete = self.find_by_id_or_404(id_)

        # Delete object from db.
        self.db.delete(model_to_delete)
        self.db.commit()

    def add_obj(self, new_data: BaseSchema) -> BaseModel:
        """
        Adds new object into db.
        :param new_data: object data.
        :return: added object.
        """
        # Find the max id for this model.
        max_obj_id: int = self.get_max_id()

        # Create new object by model with given data.
        new_obj = self.model(id=max_obj_id + 1, **new_data.dict())

        # Save new object into db.
        self.db.add(new_obj)
        self.db.commit()
        self.db.refresh(new_obj)

        return new_obj

    def check_user_access(self) -> bool:
        """
        First checks if the model has a 'user_id'.
        If the model has no 'user_id' then returns True.
        Second checks user role.
        If the user has the 'client' role,
        then he does not get access to some functional or data.
        :return: False if 'client' role or True if other.
        """
        if not self._check_if_model_has_user_id(self.model):
            return True
        if self.user:
            match self.user.role:
                case 'client':
                    return False
                case _:
                    return True
        return True

    def _prepare_data_for_update_operation(self,
                                           old_obj: BaseModel,
                                           new_data: BaseSchema
                                           ) -> BaseSchema:
        """
        Executes all necessary checks to update the object data.
        :param old_obj: data from db.
        :param new_data: object update data.
        :return: updated data.
        """
        # Extract object data by scheme.
        old_data: BaseSchema = self.patch_schema(**old_obj.__dict__)

        # Update data.
        data_to_update: dict = new_data.dict(exclude_unset=True)  # remove fields where value is None
        if data_to_update:
            updated_data: BaseSchema = old_data.copy(update=data_to_update)  # replace only changed data
        else:
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=get_text('err_patch_no_data')
            )
        return updated_data

    def _check_param_name_in_model(self, param_name) -> NoReturn:
        """
        If the model does not have a given parameter name, then raises the error.
        """
        if not hasattr(self.model, param_name):
            raise JSONException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=get_text('err_500')
            )

    def _raise_obj_not_found(self, id_) -> NoReturn:
        """
        If there is no object with the given id in the db, then raises the error.
        """
        raise JSONException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=get_text('not_found').format(self.model_name, id_)
        )

    def _raise_param_not_found(self, param_name, param_value) -> NoReturn:
        """
        If there is no object with the given parameter in the db, then raises the error.
        """
        raise JSONException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=get_text('param_not_found').format(self.model_name,
                                                       param_name,
                                                       param_value)
        )

    @staticmethod
    def _check_if_model_has_user_id(obj: BaseModel):
        return hasattr(obj, 'user_id')
