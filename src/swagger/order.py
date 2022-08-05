from dataclasses import dataclass
from datetime import date, datetime as dt
from typing import Optional, Type, Any, Literal

from fastapi import Query, status

from src.schemes.order.base_schemes import (OrderGetSchema,
                                            OrderPatchSchema,
                                            OrderPostSchema)
from src.schemes.order.response_schemes import (OrderResponsePatchSchema,
                                                OrderResponseDeleteSchema,
                                                OrderResponsePostSchema)


@dataclass
class OrderInterfaceGetAll:
    start_datetime: dt | date = Query(
        default=None,
        description="Date or datetime obj",
        example='2022-01-01'
    )
    end_datetime: dt | date = Query(
        default=None,
        description="Date or datetime obj",
        example='2022-01-01T13:00'
    )
    status: Literal['processing'] | Literal['confirmed'] = Query(
        default=None,
        description="'processing' or 'confirmed'",
        example='processing'
    )
    cost: float = Query(default=None, description="Less or equal")
    user_id: int = Query(default=None, description="Client ID")


@dataclass
class OrderInterfacePatch:
    data: OrderPatchSchema


@dataclass
class OrderInterfacePost:
    data: OrderPostSchema


@dataclass
class OrderOutputGetAll:
    summary: Optional[str] = 'Get all orders by parameters'
    description: Optional[str] = (
        "**Returns** all orders from db by **parameters**. <br />"
        "Available to all **confirmed users.** <br />"
        "<br />"
        "**Non-superuser behavior:** <br />"
        "It will only find orders associated with the user id, "
        "else return empty list."
    )
    response_model: Optional[Type[Any]] = list[OrderGetSchema]
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'List of orders'


@dataclass
class OrderOutputGet:
    summary: Optional[str] = 'Get order by order id'
    description: Optional[str] = (
        "**Returns** order from db by **order id**. <br />"
        "Available to all **confirmed users.** <br />"
        "<br />"
        "**Non-superuser behavior:** <br />"
        "It will return the order only if the order is associated with this user, "
        "else return None."
    )
    response_model: Optional[Type[Any]] = OrderGetSchema
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'Order data'


@dataclass
class OrderOutputDelete:
    summary: Optional[str] = 'Delete order by order id'
    description: Optional[str] = (
        "**Deletes** order from db by **order id**. <br />"
        "Available to all **confirmed users.** <br />"
        "<br />"
        "**Non-superuser behavior:** <br />"
        "It will delete the order only if the order is associated with this user, "
        "else raise exception that there is no such order."
    )
    response_model: Optional[Type[Any]] = OrderResponseDeleteSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderOutputPatch:
    summary: Optional[str] = 'Patch order by order id'
    description: Optional[str] = (
        "**Updates** order from db by **order id**. <br />"
        "Available to all **confirmed users.** <br />"
        "<br />"
        "**Non-superuser behavior:** <br />"
        "It will patch the order only if the order is associated with this user, "
        "else raise exception that there is no such order."
    )
    response_model: Optional[Type[Any]] = OrderResponsePatchSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderOutputPost:
    summary: Optional[str] = 'Add new order'
    description: Optional[str] = (
        "**Adds** new order into db. <br />"
        "Available to all **confirmed users.** <br />"
    )
    response_model: Optional[Type[Any]] = OrderResponsePostSchema
    status_code: Optional[int] = status.HTTP_201_CREATED
