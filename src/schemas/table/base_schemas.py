from typing import Literal

from pydantic import BaseModel


class TableBaseSchema(BaseModel):
    type: Literal['standard'] | Literal['private'] | Literal["vip_room"]
    number_of_seats: int
    price_per_hour: float


class TablePutSchema(TableBaseSchema):
    pass


class TableDeleteSchema(TableBaseSchema):
    pass


class TablePostSchema(TableBaseSchema):
    pass


class TableGetSchema(TableBaseSchema):
    id: int

    class Config:
        orm_mode = True
