from dataclasses import dataclass, asdict
from datetime import datetime as dt, date
from typing import Literal

from fastapi import Depends, Query, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.models.user import UserModel
from src.models.order import OrderModel
from src.schemes.order.base_schemes import (OrderPatchSchema,
                                            OrderPostSchema)
from src.crud_operations.order import OrderOperation
from src.swagger.order import (OrderSwaggerForGetAll,
                               OrderSwaggerForGet,
                               OrderSwaggerForPatch,
                               OrderSwaggerForDelete,
                               OrderSwaggerForPost)
from src.utils.dependencies.db import get_db
from src.utils.dependencies.auth import (get_current_admin_or_superuser,
                                         get_current_confirmed_user)
from src.utils.responses.main import get_text

# Unfortunately attribute 'prefix' in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['order'])


@dataclass
class OrderInterfaceForGetAll:
    start_datetime: dt | date = Query(default=None, description="YYYY-mm-ddTHH:MM")
    end_datetime: dt | date = Query(default=None, description="YYYY-mm-ddTHH:MM")
    status: Literal['processing'] | Literal['confirmed'] = Query(
        default=None, description="'processing' or 'confirmed'"
    )
    cost: float = Query(default=None, description="Order cost")
    user_id: int = Query(default=None, description="Client ID")


@dataclass
class OrderInterfaceForPatch:
    data: OrderPatchSchema
    id: int = Path(..., ge=1)
    admin: UserModel = Depends(get_current_admin_or_superuser)


@dataclass
class OrderInterfaceForDelete:
    id: int = Path(..., ge=1)
    admin: UserModel = Depends(get_current_admin_or_superuser)


@dataclass
class OrderInterfaceForPost:
    data: OrderPostSchema
    admin: UserModel = Depends(get_current_admin_or_superuser)


@cbv(router)
class Order:
    db: Session = Depends(get_db)
    user: UserModel = Depends(get_current_confirmed_user)

    def __init__(self):
        self.order_operation = OrderOperation(db=self.db, user=self.user)

    @router.get('/orders/', **asdict(OrderSwaggerForGetAll()))
    def get_all_orders(self,
                       order: OrderInterfaceForGetAll = Depends(OrderInterfaceForGetAll)
                       ) -> list[OrderModel] | list[None]:
        """
        Returns all orders from db by parameters.
        Available to everyone.
        """
        params: dict = {
            'start_datetime': order.start_datetime,
            'end_datetime': order.end_datetime,
            'status': order.status,
            'cost': order.cost,
            'user_id': order.user_id
        }
        return self.order_operation.find_all_by_params(**params)

    @router.get("/orders/{order_id}", **asdict(OrderSwaggerForGet()))
    def get_order(self, order_id: int = Path(..., ge=1)) -> OrderModel | None:
        """
        Returns one order from db by order id.
        Available to everyone.
        """
        return self.order_operation.find_by_id(order_id)

    @router.patch("/orders/{order_id}", **asdict(OrderSwaggerForPatch()))
    def patch_order(self,
                    order: OrderInterfaceForPatch = Depends(OrderInterfaceForPatch)
                    ) -> JSONResponse:
        """
        Updates order data.
        Only available to admins.
        """
        self.order_operation.update_obj(order.id, order.data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('patch').format(self.order_operation.model_name, order.id)}
        )

    @router.delete("/orders/{order_id}", **asdict(OrderSwaggerForDelete()))
    def delete_order(self,
                     order: OrderInterfaceForDelete = Depends(OrderInterfaceForDelete)
                     ) -> JSONResponse:
        """
        Deletes order from db by order id.
        Only available to admins.
        """
        self.order_operation.delete_obj(order.id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('delete').format(self.order_operation.model_name, order.id)}
        )

    @router.post("/orders/create", **asdict(OrderSwaggerForPost()))
    def add_order(self,
                  order: OrderInterfaceForPost = Depends(OrderInterfaceForPost)
                  ) -> JSONResponse:
        """
        Adds new order into db.
        Only available to admins.
        """
        order = self.order_operation.add_obj(order.data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": get_text('post').format(self.order_operation.model_name, order.id)}
        )
