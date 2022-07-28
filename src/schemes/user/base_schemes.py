from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=5, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=9, max_length=15, regex=r'^([\d]+)$')
    role: Literal['superuser'] | Literal['admin'] | Literal['client']


class UserPatchSchema(UserBaseSchema):
    username: str | None = Field(None, min_length=5, max_length=100)
    email: EmailStr | None
    phone: str | None = Field(None, min_length=9, max_length=15, regex=r'^([\d]+)$')
    role: Literal['superuser'] | Literal['admin'] | Literal['client'] | None
    status: Literal['confirmed'] | Literal['unconfirmed'] | None


class UserDeleteSchema(UserBaseSchema):
    pass


class UserPostSchema(UserBaseSchema):
    password: str = Field(..., min_length=10, max_length=100)


class UserGetSchema(UserBaseSchema):
    id: int
    status: Literal['confirmed'] | Literal['unconfirmed']

    class Config:
        orm_mode = True
