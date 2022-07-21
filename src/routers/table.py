from fastapi import Depends, Query, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from ..models.table import TableModel
from ..schemas.table.base_schemas import (TableGetSchema,
                                          TablePutSchema,
                                          TablePostSchema)
from ..schemas.table.response_schemas import (TableResponsePutSchema,
                                              TableResponseDeleteSchema,
                                              TableResponsePostSchema)
from src.crud_operations.table import TableOperation
from src.utils.dependencies import get_db
from src.utils.responses.main import get_text

router = InferringRouter(prefix='/tables', tags=['table'])


@cbv(router)
class Table:
    db: Session = Depends(get_db)

    def __init__(self):
        self.table_operation = TableOperation(model=TableModel,
                                              response_elem_name='table',
                                              db=self.db)

    @router.get("/", response_model=list[TableGetSchema], status_code=status.HTTP_200_OK)
    def get_all_tables(self,
                       type: str = Query(default=None,
                                         description="Table type"),
                       number_of_seats: int = Query(default=None,
                                                    description="More or equal"),
                       price_per_hour: float = Query(default=None,
                                                     description="Less or equal")):
        return self.table_operation.find_all_by_params(type=type,
                                                       number_of_seats=number_of_seats,
                                                       price_per_hour=price_per_hour)

    @router.get("/{table_id}", response_model=TableGetSchema, status_code=status.HTTP_200_OK)
    def get_table(self, table_id: int = Path(..., ge=1)):
        return self.table_operation.find_by_id_or_404(table_id)

    @router.put("/{table_id}", response_model=TableResponsePutSchema, status_code=status.HTTP_200_OK)
    def put_table(self, table: TablePutSchema, table_id: int = Path(..., ge=1)):
        self.table_operation.update_model(table_id, table)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('put').format(
                                self.table_operation.response_elem_name, table_id
                            )})

    @router.delete("/{table_id}", response_model=TableResponseDeleteSchema, status_code=status.HTTP_200_OK)
    def delete_table(self, table_id: int):
        self.table_operation.delete_model(table_id)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('delete').format(
                                self.table_operation.response_elem_name, table_id
                            )})

    @router.post("/create", response_model=TableResponsePostSchema, status_code=status.HTTP_201_CREATED)
    def add_table(self, table: TablePostSchema):
        table = self.table_operation.add_model(table)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": get_text('post').format(
                                self.table_operation.response_elem_name, table.id
                            )})