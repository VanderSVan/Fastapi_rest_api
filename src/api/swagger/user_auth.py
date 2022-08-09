from dataclasses import dataclass
from typing import Optional, Type, Any

from fastapi import status

from src.api.schemes.user.base_schemes import UserGetSchema
from src.api.schemes.user.response_schemes import (UserResponseConfirmEmailSchema,
                                                   UserResponseResetPasswordSchema,
                                                   UserResponseConfirmResetPasswordSchema)
from src.api.schemes.jwt.response_schemes import TokenResponseSchema


@dataclass
class UserAuthOutputGetCurrentUser:
    summary: Optional[str] = 'Get current user info'
    description: Optional[str] = (
        "**Returns** current user info. <br />"
        "Available to all **confirmed users.**"
    )
    response_model: Optional[Type[Any]] = UserGetSchema
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'Current user'


@dataclass
class UserAuthOutputConfirmEmail:
    summary: Optional[str] = 'Confirm email address'
    description: Optional[str] = (
        "**Confirms** user's email. <br />"
        "**Accessible to all.** <br />"
        "**sign**: it is encoded user data, such as a username."
    )
    response_model: Optional[Type[Any]] = UserResponseConfirmEmailSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class UserAuthOutputResetPassword:
    summary: Optional[str] = "Reset user's password"
    description: Optional[str] = (
        "**Resets** user's password. <br />"
        "Available to all **confirmed users.**"
    )
    response_model: Optional[Type[Any]] = UserResponseResetPasswordSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class UserAuthOutputGetToken:
    summary: Optional[str] = 'Get user token via login'
    description: Optional[str] = (
        "**Gets** user token by entering your username and password. <br />"
        "**Accessible to all.**"
    )
    response_model: Optional[Type[Any]] = TokenResponseSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class UserAuthOutputRegister:
    summary: Optional[str] = 'Register a new user'
    description: Optional[str] = (
        "**Gets** new user data and saves it into db. <br />"
        "**Accessible to all.**"
    )
    response_model: Optional[Type[Any]] = UserGetSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class UserAuthOutputConfirmNewPassword:
    summary: Optional[str] = "Confirm new user's password"
    description: Optional[str] = (
        "**Gets** the user's new password and saves it in the database. <br />"
        "**Accessible to all.** <br />"
        "**sign**: it is encoded user data, such as a username."
    )
    response_model: Optional[Type[Any]] = UserResponseConfirmResetPasswordSchema
    status_code: Optional[int] = status.HTTP_200_OK

