from dataclasses import asdict

from fastapi import Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.models.user import UserModel
from src.models.order import OrderModel
from src.crud_operations.order import OrderOperation
from src.swagger.order import (
    OrderInterfaceGetAll,
    OrderInterfacePatch,
    OrderInterfacePost,

    OrderOutputGetAll,
    OrderOutputGet,
    OrderOutputPatch,
    OrderOutputDelete,
    OrderOutputPost
)
from src.utils.dependencies.db import get_db
from src.utils.dependencies.auth import get_current_confirmed_user
from src.utils.responses.main import get_text

# Unfortunately attribute 'prefix' in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['order'])


@cbv(router)
class Order:
    db: Session = Depends(get_db)
    user: UserModel = Depends(get_current_confirmed_user)

    def __init__(self):
        self.order_operation = OrderOperation(db=self.db, user=self.user)

    @router.get('/orders/', **asdict(OrderOutputGetAll()))
    def get_all_orders(self,
                       order: OrderInterfaceGetAll = Depends(OrderInterfaceGetAll)
                       ) -> list[OrderModel] | list[None]:
        """
        Returns all orders from db by parameters.
        Available to all confirmed users.
        """
        params: dict = {
            'start_datetime': order.start_datetime,
            'end_datetime': order.end_datetime,
            'status': order.status,
            'cost': order.cost,
            'user_id': order.user_id
        }
        return self.order_operation.find_all_by_params(**params)

    @router.get("/orders/{order_id}", **asdict(OrderOutputGet()))
    def get_order(self, order_id: int = Path(..., ge=1)) -> OrderModel | None:
        """
        Returns one order from db by order id.
        Available to all confirmed users.
        """
        return self.order_operation.find_by_id(order_id)

    @router.patch("/orders/{order_id}", **asdict(OrderOutputPatch()))
    def patch_order(self,
                    order_id: int = Path(..., ge=1),
                    order: OrderInterfacePatch = Depends(OrderInterfacePatch)
                    ) -> JSONResponse:
        """
        Updates order data.
        Only available to admins.
        """
        self.order_operation.update_obj(order_id, order.data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('patch').format(self.order_operation.model_name, order_id)}
        )

    @router.delete("/orders/{order_id}", **asdict(OrderOutputDelete()))
    def delete_order(self, order_id: int = Path(..., ge=1)) -> JSONResponse:
        """
        Deletes order from db by order id.
        Only available to admins.
        """
        self.order_operation.delete_obj(order_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('delete').format(self.order_operation.model_name, order_id)}
        )

    @router.post("/orders/create", **asdict(OrderOutputPost()))
    def add_order(self,
                  order: OrderInterfacePost = Depends(OrderInterfacePost)
                  ) -> JSONResponse:
        """
        Adds new order into db.
        Available to all confirmed users.
        """
        order = self.order_operation.add_obj(order.data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": get_text('post').format(self.order_operation.model_name, order.id)}
        )
