from typing import NoReturn
from fastapi import status
from fastapi.security import OAuth2PasswordBearer

from src.api.models.user import UserModel
from src.api.crud_operations.user import UserOperation
from src.utils.exceptions import JSONException
from src.utils.response_generation.main import get_text
from src.utils.auth_utils.password_cryptograph import PasswordCryptographer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserAuthOperation(UserOperation):
    def authenticate_user(self, username: str, password: str) -> UserModel:
        user = self.find_by_param_or_404('username', username)
        if not PasswordCryptographer.verify(password, user.hashed_password):
            raise JSONException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message=get_text('authenticate_failed'),
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user

    def confirm_user_email(self, username: str) -> UserModel:
        # Get user object from db.
        user_obj: UserModel = self.find_by_param_or_404('username', username)

        # Check user status.
        self._check_user_status(user_obj)

        # Update user status.
        user_obj.status = 'confirmed'
        updated_user_obj = user_obj

        # Save new user data.
        self.db.commit()
        self.db.refresh(updated_user_obj)

        return updated_user_obj

    def confirm_reset_password(self, username: str, new_password):
        # Get user object from db.
        user_obj: UserModel = self.find_by_param_or_404('username', username)

        # Update user password.
        user_obj.hashed_password = PasswordCryptographer.bcrypt(new_password)
        updated_user_obj = user_obj

        # Save new user data.
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
