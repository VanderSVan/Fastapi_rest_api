from sqlalchemy.orm import Session
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer

from src.api.models.user import UserModel
from src.api.schemes.jwt.base_shemes import TokenSchema
from src.api.crud_operations.user_auth import UserAuthOperation
from src.utils.exceptions import JSONException
from src.utils.response_generation.main import get_text
from src.utils.auth_utils.jwt import JWT
from src.api.dependencies.db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)
                     ) -> UserModel:
    """Gets the current user data from the JWT"""
    payload: dict = JWT.extract_payload_from_token(token)
    username: str = payload.get("sub")

    if username is None:
        raise JSONException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token_data = TokenSchema(username=username)

    return UserAuthOperation(db).find_by_param_or_404('username', token_data.username)


def get_current_confirmed_user(current_user: UserModel = Depends(get_current_user)
                               ) -> UserModel:
    """
    Gets the current user data from the JWT and checks the user's status.
    If status is 'unconfirmed' raises Unauthorized exception.
    """
    match current_user.status:
        case 'unconfirmed':
            raise JSONException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message=get_text('email_not_confirmed')
            )
        case _:
            return current_user


def get_current_admin_or_superuser(current_user: UserModel = Depends(get_current_user)
                                   ) -> UserModel:
    """
    Gets the current user data from the JWT and checks the user's role.
    If role is 'client' raises Forbidden exception.
    """
    match current_user.role:
        case 'client':
            raise JSONException(
                status_code=status.HTTP_403_FORBIDDEN,
                message=get_text('forbidden_request')
            )
        case _:
            return current_user
