from datetime import datetime as dt
from typing import Literal, Any

from pydantic import BaseModel, Field, root_validator

from ..table.base_schemes import TableGetSchema
from ..validators.order import OrderBaseValidator, OrderPatchValidator, OrderPostValidator


class OrderBaseSchema(BaseModel):
    start_datetime: dt = Field(dt.utcnow().strftime('%Y-%m-%dT%H:%M'))
    end_datetime: dt = Field(dt.utcnow().strftime('%Y-%m-%dT%H:%M'))
    status: Literal['processing'] | Literal['confirmed']
    user_id: int = Field(..., ge=1)


class OrderPatchSchema(OrderBaseSchema):
    start_datetime: dt | None = Field(dt.utcnow().strftime('%Y-%m-%dT%H:%M'))
    end_datetime: dt | None = Field(dt.utcnow().strftime('%Y-%m-%dT%H:%M'))
    status: Literal['processing'] | Literal['confirmed'] | None
    cost: float | None
    user_id: int | None
    add_tables: list[int] | None
    delete_tables: list[int] | None

    @root_validator(pre=True)
    def order_base_validate(cls, values):
        validator = OrderBaseValidator(values)
        return validator.validate_data()

    @root_validator()
    def order_post_validate(cls, values):
        validator = OrderPatchValidator(values)
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
        validator = OrderPostValidator(values)
        return validator.validate_data()


class OrderGetSchema(OrderBaseSchema):
    id: int
    cost: Any
    tables: list[TableGetSchema]

    class Config:
        orm_mode = True
