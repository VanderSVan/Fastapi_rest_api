from typing import Literal

from pydantic import Field

from src.api.schemes.table.base_schemes import TableGetSchema
from src.api.schemes.order.base_schemes import OrderBaseSchema


class ShortOrderSchema(OrderBaseSchema):
    """Order schema without nested tables."""
    id: int | None = Field(None, ge=1)
    user_id: int | None = Field(None, ge=1)
    status: Literal['processing'] | Literal['confirmed'] | None
    cost: float | None

    class Config:
        orm_mode = True
        fields = {
            'tables': {'exclude': ..., }
        }


class FullTableGetSchema(TableGetSchema):
    """Full info is available"""
    orders: list[ShortOrderSchema]

    class Config:
        orm_mode = True
