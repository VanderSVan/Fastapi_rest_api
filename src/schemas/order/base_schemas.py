from datetime import datetime

from pydantic import BaseModel, validator
from fastapi import Request


class OrderBaseSchema(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    is_approved: bool = False
    cost: float
    Order_id: int
    tables: list[int]


# class OrderCreateSchema(OrderBaseSchema):
# 
#     @validator("tables")
#     def check_tables(cls, tables):
#         print("ZALUPA" if Request == 'POST' else Request.method)
#         print("hebalse" if tables else "nihuebles")
#         return "hebalse" if tables else "nihuebles"

class OrderPutSchema(OrderBaseSchema):
    pass


class OrderDeleteSchema(OrderBaseSchema):
    pass


class OrderPostSchema(OrderBaseSchema):
    pass


class OrderGetSchema(OrderBaseSchema):
    id: int

    class Config:
        orm_mode = True
