from dataclasses import dataclass
from typing import Literal, Optional, Type, Any

from fastapi import Query, Path, Body, status

from src.api.schemes.user.base_schemes import (UserGetSchema,
                                               UserPatchSchema,
                                               UserPostSchema)
from src.api.schemes.user.response_schemes import (UserResponsePatchSchema,
                                                   UserResponseDeleteSchema,
                                                   UserResponsePostSchema)


@dataclass
class UserInterfaceGetAll:
    phone: str = Query(default=None, description="Phone number")
    status: Literal['confirmed'] | Literal['unconfirmed'] = Query(
        default=None, description="'confirmed' or 'unconfirmed'"
    )
    
    
@dataclass
class UserInterfacePatch:
    user_id: int = Path(..., ge=1)
    data: UserPatchSchema = Body(..., example={
        "username": "some_username",
        "email": "user@example.com",
        "phone": "123456789",
        "role": "client",
        "status": "unconfirmed"
    })


@dataclass
class UserInterfacePost:
    data: UserPostSchema = Body(..., example={
        "username": "some_username",
        "email": "user@example.com",
        "phone": "123456789",
        "role": "client",
        "password": "some_strong_password"
    })


@dataclass
class UserOutputGetAll:
    summary: Optional[str] = 'Get all users by parameters'
    description: Optional[str] = (
        "**Returns** all users from db by **parameters**. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = list[UserGetSchema]
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'List of users'
    

@dataclass
class UserOutputGet:
    summary: Optional[str] = 'Get user by user id'
    description: Optional[str] = (
        "**Returns** user from db by **user id**. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = UserGetSchema
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'User data'
    

@dataclass
class UserOutputDelete:
    summary: Optional[str] = 'Delete user by user id'
    description: Optional[str] = (
        "**Deletes** user from db by **user id**. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = UserResponseDeleteSchema
    status_code: Optional[int] = status.HTTP_200_OK
    

@dataclass
class UserOutputPatch:
    summary: Optional[str] = 'Patch user by user id'
    description: Optional[str] = (
        "**Updates** user from db by **user id**. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = UserResponsePatchSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class UserOutputPost:
    summary: Optional[str] = 'Post user by user id'
    description: Optional[str] = (
        "**Adds** new user into db. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = UserResponsePostSchema
    status_code: Optional[int] = status.HTTP_201_CREATED

