from datetime import datetime as dt
from datetime import timedelta as td
from typing import Literal, Any

from pydantic import BaseModel, Field, root_validator

from src.schemes.validators.order import OrderBaseValidator, OrderPostOrPatchValidator
from src.schemes.table.base_schemes import TableGetSchema


class OrderBaseSchema(BaseModel):
    start_datetime: dt = Field(..., example=dt.utcnow().strftime('%Y-%m-%dT%H:%M'))
    end_datetime: dt = Field(..., example=(dt.utcnow() + td(hours=1)).strftime('%Y-%m-%dT%H:%M'))
    user_id: int = Field(..., ge=1)


class OrderPatchSchema(OrderBaseSchema):
    start_datetime: dt | None = Field(None, example=dt.utcnow().strftime('%Y-%m-%dT%H:%M'))
    end_datetime: dt | None = Field(None, example=(dt.utcnow() + td(hours=1)).strftime('%Y-%m-%dT%H:%M'))
    status: Literal['processing'] | Literal['confirmed'] | None
    cost: float | None
    user_id: int | None = Field(None, ge=1)
    add_tables: list[int] | None = Field(None, ge=1)
    delete_tables: list[int] | None = Field(None, ge=1)

    @root_validator(pre=True)
    def order_base_validate(cls, values):
        validator = OrderBaseValidator(values)
        return validator.validate_data()

    @root_validator()
    def order_post_validate(cls, values):
        validator = OrderPostOrPatchValidator(values)
        return validator.validate_data()


class OrderDeleteSchema(OrderBaseSchema):
    pass


class OrderPostSchema(OrderBaseSchema):
    tables: list[int] = Field(..., ge=1)

    @root_validator(pre=True)
    def order_base_validate(cls, values):
        validator = OrderBaseValidator(values)
        return validator.validate_data()

    @root_validator()
    def order_post_validate(cls, values):
        validator = OrderPostOrPatchValidator(values)
        return validator.validate_data()


class OrderGetSchema(OrderBaseSchema):
    id: int
    status: Literal['processing'] | Literal['confirmed']
    cost: Any
    tables: list[TableGetSchema]

    class Config:
        orm_mode = True
