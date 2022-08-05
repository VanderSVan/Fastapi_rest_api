from dataclasses import dataclass
from datetime import date, datetime as dt
from typing import Optional, Type, Any, Literal

from fastapi import Depends, Query, status

from src.models.user import UserModel
from src.schemes.order.base_schemes import (OrderGetSchema,
                                            OrderPatchSchema,
                                            OrderPostSchema)
from src.schemes.order.response_schemes import (OrderResponsePatchSchema,
                                                OrderResponseDeleteSchema,
                                                OrderResponsePostSchema)
from src.utils.dependencies.auth import get_current_admin_or_superuser


@dataclass
class OrderInterfaceGetAll:
    start_datetime: dt | date = Query(default=None,
                                      description="Time or datetime obj",
                                      example='2022-01-01')
    end_datetime: dt | date = Query(default=None,
                                    description="Time or datetime obj",
                                    example='2022-01-01T13:00')
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
    response_model: Optional[Type[Any]] = list[OrderGetSchema]
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderOutputGet:
    response_model: Optional[Type[Any]] = OrderGetSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderOutputPatch:
    response_model: Optional[Type[Any]] = OrderResponsePatchSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderOutputDelete:
    response_model: Optional[Type[Any]] = OrderResponseDeleteSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderOutputPost:
    response_model: Optional[Type[Any]] = OrderResponsePostSchema
    status_code: Optional[int] = status.HTTP_201_CREATED

