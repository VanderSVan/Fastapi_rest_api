from datetime import datetime as dt

from fastapi import Depends, Query, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from ..models.order import OrderModel
from ..schemas.order.base_schemas import (OrderGetSchema,
                                          OrderPutSchema,
                                          OrderPostSchema)
from ..schemas.order.response_schemas import (OrderResponsePutSchema,
                                              OrderResponseDeleteSchema,
                                              OrderResponsePostSchema)
from src.crud_operations.order import OrderOperation
from src.utils.dependencies import get_db
from src.utils.responses.main import get_text

router = InferringRouter(prefix='/orders', tags=['order'])


@cbv(router)
class Order:
    db: Session = Depends(get_db)

    def __init__(self):
        self.order_operation = OrderOperation(model=OrderModel, response_elem_name='order', db=self.db)

    @router.get("/", response_model=list[OrderGetSchema], status_code=status.HTTP_200_OK)
    def get_all_orders(self,
                       start_datetime: dt = Query(default=None,
                                                  description="YYYY-mm-ddTHH:MM:SS"),
                       end_datetime: dt = Query(default=None,
                                                description="YYYY-mm-ddTHH:MM:SS"),
                       is_approved: bool = Query(default=None,
                                                 description="Order confirmation"),
                       cost: float = Query(default=None,
                                           description="Order cost"),
                       client_id: int = Query(default=None,
                                              description="Client ID"),
                       ):
        return self.order_operation.find_all_by_params(start_datetime=start_datetime,
                                                       end_datetime=end_datetime,
                                                       is_approved=is_approved,
                                                       cost=cost,
                                                       client_id=client_id)

    @router.get("/{order_id}", response_model=OrderGetSchema, status_code=status.HTTP_200_OK)
    def get_order(self, order_id: int = Path(..., ge=1)):
        return self.order_operation.find_by_id_or_404(order_id)

    @router.put("/{order_id}", response_model=OrderResponsePutSchema, status_code=status.HTTP_200_OK)
    def put_order(self, order: OrderPutSchema, order_id: int = Path(..., ge=1)):
        self.order_operation.update_model(order_id, order)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('put').format(
                                self.order_operation.response_elem_name, order_id
                            )})

    @router.delete("/{order_id}", response_model=OrderResponseDeleteSchema, status_code=status.HTTP_200_OK)
    def delete_order(self, order_id: int):
        self.order_operation.delete_model(order_id)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('delete').format(
                                self.order_operation.response_elem_name, order_id
                            )})

    @router.post("/create", response_model=OrderResponsePostSchema, status_code=status.HTTP_200_OK)
    def add_order(self, order: OrderPostSchema):
        order = self.order_operation.add_model(order)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": get_text('post').format(
                                self.order_operation.response_elem_name, order.id
                            )})
