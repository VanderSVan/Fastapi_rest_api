from src.schemes.table.base_schemes import TableGetSchema
from src.schemes.order.base_schemes import OrderGetSchema


class ShortOrderSchema(OrderGetSchema):
    """Only order time is available."""

    class Config:
        orm_mode = True
        fields = {
            'status': {'exclude': ..., },
            'user_id': {'exclude': ..., },
            'id': {'exclude': ..., },
            'cost': {'exclude': ..., },
            'tables': {'exclude': ..., }
        }


class ClientTableGetSchema(TableGetSchema):
    """Only order time is available."""
    orders: list[ShortOrderSchema]

    class Config:
        orm_mode = True


class AdminTableGetSchema(TableGetSchema):
    """Full info is available"""
    orders: list[OrderGetSchema]

    class Config:
        orm_mode = True
