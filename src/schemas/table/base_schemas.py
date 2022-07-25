from typing import Literal

from pydantic import BaseModel, Field


class TableBaseSchema(BaseModel):
    type: Literal['standard'] | Literal['private'] | Literal["vip_room"]
    number_of_seats: int = Field(..., ge=1)
    price_per_hour: float


class TablePatchSchema(TableBaseSchema):
    pass


class TableDeleteSchema(TableBaseSchema):
    pass


class TablePostSchema(TableBaseSchema):
    pass


class TableGetSchema(TableBaseSchema):
    id: int = Field(..., ge=1)

    class Config:
        orm_mode = True
