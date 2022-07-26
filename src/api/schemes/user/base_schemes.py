from typing import Literal

from pydantic import (BaseModel as BaseSchema,
                      EmailStr,
                      Field,
                      root_validator)

from src.api.schemes.validators.user import UserPasswordValidator


class UserBaseSchema(BaseSchema):
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
    password: str = Field(..., min_length=8, max_length=30)


class UserGetSchema(UserBaseSchema):
    id: int
    status: Literal['confirmed'] | Literal['unconfirmed']

    class Config:
        orm_mode = True


class UserResetPasswordSchema(BaseSchema):
    password: str = Field(
        ...,
        title='Password',
        min_length=8,
        max_length=30,
    )
    password_confirm: str = Field(
        ...,
        title='Repeat your password',
        min_length=8,
        max_length=30,
    )

    @root_validator()
    def user_password_validate(cls, values):
        validator = UserPasswordValidator(values)
        return validator.validate_data()


