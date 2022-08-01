from datetime import datetime as dt, date
from typing import Literal

from fastapi import Depends, Query, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.models.user import UserModel
from src.models.order import OrderModel
from src.schemes.order.base_schemes import (OrderGetSchema,
                                            OrderPatchSchema,
                                            OrderPostSchema)
from src.schemes.order.response_schemes import (OrderResponsePatchSchema,
                                                OrderResponseDeleteSchema,
                                                OrderResponsePostSchema)
from src.crud_operations.order import OrderOperation
from src.utils.dependencies.db import get_db
from src.utils.dependencies.auth import (get_current_admin_or_superuser,
                                         get_current_confirmed_user)
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

    ###############################################################
    @router.get("/orders/",
                response_model=list[OrderGetSchema],
                status_code=status.HTTP_200_OK
                )
    def get_all_orders(
            self,
            start_datetime: dt | date = Query(default=None, description="YYYY-mm-ddTHH:MM"),
            end_datetime: dt | date = Query(default=None, description="YYYY-mm-ddTHH:MM"),
            status: Literal['processing'] | Literal['confirmed'] = Query(
                default=None, description="'processing' or 'confirmed'"
            ),
            cost: float = Query(default=None, description="Order cost"),
            user_id: int = Query(default=None, description="Client ID")
    ) -> list[OrderModel] | list[None]:
        """
        Returns all orders from db by parameters.
        Available to everyone.
        """
        return self.order_operation.find_all_by_params(start_datetime=start_datetime,
                                                       end_datetime=end_datetime,
                                                       status=status,
                                                       cost=cost,
                                                       user_id=user_id)

    ###############################################################
    @router.get("/orders/{order_id}",
                response_model=OrderGetSchema,
                status_code=status.HTTP_200_OK
                )
    def get_order(self,
                  order_id: int = Path(..., ge=1),
                  ) -> OrderModel | None:
        """
        Returns one order from db by order id.
        Available to everyone.
        """
        return self.order_operation.find_by_id(order_id)

    ###############################################################
    @router.patch("/orders/{order_id}",
                  response_model=OrderResponsePatchSchema,
                  status_code=status.HTTP_200_OK
                  )
    def patch_order(self,
                    order: OrderPatchSchema,
                    order_id: int = Path(..., ge=1),
                    admin: UserModel = Depends(get_current_admin_or_superuser)
                    ) -> JSONResponse:
        """
        Updates order data.
        Only available to admins.
        """
        self.order_operation.update_obj(order_id, order)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('patch').format(
                                self.order_operation.model_name, order_id
                            )})

    ###############################################################
    @router.delete("/orders/{order_id}",
                   response_model=OrderResponseDeleteSchema,
                   status_code=status.HTTP_200_OK,
                   )
    def delete_order(self,
                     order_id: int,
                     admin: UserModel = Depends(get_current_admin_or_superuser)
                     ) -> JSONResponse:
        """
        Deletes order from db by order id.
        Only available to admins.
        """
        self.order_operation.delete_obj(order_id)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('delete').format(
                                self.order_operation.model_name, order_id
                            )})

    ###############################################################
    @router.post("/orders/create",
                 response_model=OrderResponsePostSchema,
                 status_code=status.HTTP_200_OK
                 )
    def add_order(self,
                  order: OrderPostSchema,
                  admin: UserModel = Depends(get_current_admin_or_superuser)
                  ) -> JSONResponse:
        """
        Adds new order into db.
        Only available to admins.
        """
        order = self.order_operation.add_obj(order)

        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": get_text('post').format(
                                self.order_operation.model_name, order.id
                            )})
