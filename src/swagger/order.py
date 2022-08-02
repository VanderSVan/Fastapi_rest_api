from dataclasses import dataclass
from typing import Optional, Type, Any

from fastapi import status

from src.schemes.order.base_schemes import OrderGetSchema
from src.schemes.order.response_schemes import (OrderResponsePatchSchema,
                                                OrderResponseDeleteSchema,
                                                OrderResponsePostSchema)


@dataclass
class OrderSwaggerForGetAll:
    response_model: Optional[Type[Any]] = list[OrderGetSchema]
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderSwaggerForGet:
    response_model: Optional[Type[Any]] = OrderGetSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderSwaggerForPatch:
    response_model: Optional[Type[Any]] = OrderResponsePatchSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderSwaggerForDelete:
    response_model: Optional[Type[Any]] = OrderResponseDeleteSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class OrderSwaggerForPost:
    response_model: Optional[Type[Any]] = OrderResponsePostSchema
    status_code: Optional[int] = status.HTTP_201_CREATED

