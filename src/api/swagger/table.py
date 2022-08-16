from dataclasses import dataclass
from datetime import date, datetime as dt
from typing import Optional, Type, Any

from fastapi import Query, Path, Body, Depends, status

from src.api.models.user import UserModel
from src.api.schemes.table.base_schemes import (TablePatchSchema,
                                                TablePostSchema)
from src.api.schemes.relationships.orders_tables import FullTableGetSchema
from src.api.schemes.table.response_schemes import (TableResponsePatchSchema,
                                                    TableResponseDeleteSchema,
                                                    TableResponsePostSchema)
from src.api.dependencies.auth import get_current_admin_or_superuser


@dataclass
class TableInterfaceGetAll:
    type: str = Query(default=None, description='Table type')
    number_of_seats: int = Query(default=None, description='Less or equal')
    price_per_hour: float = Query(default=None, description='Less or equal')
    start_datetime: dt | date = Query(
        default=None,
        description="Start booking date or datetime",
        example='2022-01-01T10:00'
    )
    end_datetime: dt | date = Query(
        default=None,
        description="End booking date or datetime",
        example='2022-12-31'
    )


@dataclass
class TableInterfaceDelete:
    table_id: int = Path(..., ge=1)
    admin: UserModel = Depends(get_current_admin_or_superuser)


@dataclass
class TableInterfacePatch:
    table_id: int = Path(..., ge=1)
    data: TablePatchSchema = Body(..., example={
        "type": "standard",
        "number_of_seats": 4,
        "price_per_hour": 5000
    })
    admin: UserModel = Depends(get_current_admin_or_superuser)


@dataclass
class TableInterfacePost:
    data: TablePostSchema = Body(..., example={
        "type": "private",
        "number_of_seats": 2,
        "price_per_hour": 5000
    })
    admin: UserModel = Depends(get_current_admin_or_superuser)


@dataclass
class TableOutputGetAll:
    summary: Optional[str] = 'Get all tables by parameters'
    description: Optional[str] = (
        "**Returns** all tables from db by **parameters**. <br />"
        "Available to all **confirmed users.** <br />"
        "<br />"
        "**Non-superuser behavior:** <br />"
        "Instead of a nested full order data, "
        "it will only return the start and end datetime."

    )
    response_model: Optional[Type[Any]] = list[FullTableGetSchema]
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'List of tables'


@dataclass
class TableOutputGet:
    summary: Optional[str] = 'Get table by table id'
    description: Optional[str] = (
        "**Returns** table from db by **table id**. <br />"
        "Available to all **confirmed users.** <br />"
        "<br />"
        "**Non-superuser behavior:** <br />"
        "Instead of a nested full order data, "
        "it will only return the start and end datetime."
    )
    response_model: Optional[Type[Any]] = FullTableGetSchema
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'Table data'


@dataclass
class TableOutputDelete:
    summary: Optional[str] = 'Delete table by table id'
    description: Optional[str] = (
        "**Deletes** table from db by **table id**. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = TableResponseDeleteSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class TableOutputPatch:
    summary: Optional[str] = 'Patch table by table id'
    description: Optional[str] = (
        "**Updates** table from db by **table id**. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = TableResponsePatchSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class TableOutputPost:
    summary: Optional[str] = 'Post table by table id'
    description: Optional[str] = (
        "**Adds** new table into db. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = TableResponsePostSchema
    status_code: Optional[int] = status.HTTP_201_CREATED
