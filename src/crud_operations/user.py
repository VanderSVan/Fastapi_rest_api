from typing import NoReturn

from sqlalchemy import and_
from fastapi import status
from fastapi_mail import FastMail, MessageSchema

from .base_crud_operations import ModelOperation
from ..models.user import UserModel
from ..schemes.user.base_schemes import UserPatchSchema, UserPostSchema
from ..config import Settings
from ..services.email.main import send_confirm_email
from ..utils.exceptions import JSONException
from ..utils.responses.main import get_text
from ..utils.auth_utils.password_cryptograph import PasswordCryptographer
from ..utils.auth_utils.signature import Signer


class UserOperation(ModelOperation):
    def __init__(self, db):
        self.model = UserModel
        self.patch_schema = UserPatchSchema
        self.response_elem_name = 'user'
        self.db = db

    def find_all_by_params(self, **kwargs) -> list[UserModel]:
        phone = kwargs.get('phone')
        return (self.db
                    .query(UserModel)
                    .filter(and_(
                                 (UserModel.phone == phone
                                  if phone is not None else True),
                                )
                            )
                    .all())

    def add_model(self, new_user_schema: UserPostSchema) -> UserModel:
        # Find max user id.
        max_id: int = self.get_max_id()

        # Hash the password.
        hashed_password = PasswordCryptographer.bcrypt(new_user_schema.password)

        # Create new user object.
        new_user_obj: UserModel = self.model(
            id=max_id + 1,
            hashed_password=hashed_password,
            status='unconfirmed',
            **new_user_schema.dict(exclude={'password'})
        )

        # Save new user object into db.
        self.db.add(new_user_obj)
        self.db.commit()
        self.db.refresh(new_user_obj)
        return new_user_obj

    def confirm_user_email(self, username: str) -> UserModel:
        # Get user object from db.
        user_obj: UserModel = self.find_by_param_or_404('username', username)

        # Check user status.
        self._check_user_status(user_obj)

        # Update user status.
        user_obj.status = 'confirmed'
        updated_user_obj = user_obj

        # Save new model data.
        self.db.commit()
        self.db.refresh(updated_user_obj)
        return updated_user_obj

    @staticmethod
    def _check_user_status(user) -> NoReturn:
        if user.status == 'confirmed':
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=get_text('email_already_confirmed').format(user.username)
            )
