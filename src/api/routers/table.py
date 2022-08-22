from dataclasses import asdict

from fastapi import Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.api.models.user import UserModel
from src.api.models.table import TableModel
from src.api.schemes.relationships.orders_tables import FullTableGetSchema
from src.api.crud_operations.table import TableOperation
from src.api.swagger.table import (
    TableInterfaceGetAll,
    TableInterfaceDelete,
    TableInterfacePatch,
    TableInterfacePost,

    TableOutputGetAll,
    TableOutputGet,
    TableOutputDelete,
    TableOutputPatch,
    TableOutputPost
)
from src.api.dependencies.db import get_db
from src.api.dependencies.auth import get_current_confirmed_user
from src.utils.response_generation.main import get_text

# Unfortunately attribute 'prefix' in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['table'])


@cbv(router)
class Table:
    db: Session = Depends(get_db)
    user: UserModel = Depends(get_current_confirmed_user)

    def __init__(self):
        self.table_operation = TableOperation(db=self.db, user=self.user)

    @router.get("/tables/", **asdict(TableOutputGetAll()))
    def get_all_tables(self,
                       table: TableInterfaceGetAll = Depends()
                       ) -> list[TableModel] | list[dict] | list[None]:
        """
        Returns all tables from db by parameters.
        Available to all confirmed users.
        Non-superuser behavior:
        Instead of a nested full order data,
        it will only return the start and end datetime.
        """
        table_objs: list[TableModel] = self.table_operation.find_all_by_params(
            type=table.type,
            number_of_seats=table.number_of_seats,
            price_per_hour=table.price_per_hour,
            start_datetime=table.start_datetime,
            end_datetime=table.end_datetime
        )
        if not self.table_operation.check_user_access():
            return [
                FullTableGetSchema.from_orm(table_obj).dict(
                    exclude_unset=True,
                    exclude={'orders': {'__all__': {'user_id', 'id', 'status', 'cost'}}}
                )
                for table_obj in table_objs
            ]

        return table_objs

    @router.get("/tables/{table_id}", **asdict(TableOutputGet()))
    def get_table(self, table_id: int = Path(..., ge=1)) -> TableModel | dict | None:
        """
        Returns one table from db by table id.
        Available to all confirmed users.
        Non-superuser behavior:
        Instead of a nested full order data,
        it will only return the start and end datetime.
        """
        table_obj: TableModel = self.table_operation.find_by_id_or_404(table_id)

        if not self.table_operation.check_user_access():
            data = FullTableGetSchema.from_orm(table_obj)
            return data.dict(
                exclude_unset=True,
                exclude={'orders': {'__all__': {'user_id', 'id', 'status', 'cost'}}}
            )
        return table_obj

    @router.delete("/tables/{table_id}", **asdict(TableOutputDelete()))
    def delete_table(self,
                     table: TableInterfaceDelete = Depends()
                     ) -> JSONResponse:
        """
        Deletes table from db by table id.
        Only available to admins.
        """
        self.table_operation.delete_obj(table.table_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('delete').format(
                self.table_operation.model_name, table.table_id)}
        )

    @router.patch("/tables/{table_id}", **asdict(TableOutputPatch()))
    def patch_table(self,
                    table: TableInterfacePatch = Depends()
                    ) -> JSONResponse:
        """
        Updates table data.
        Only available to admins.
        """
        self.table_operation.update_obj(table.table_id, table.data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('patch').format(
                self.table_operation.model_name, table.table_id)}
        )

    @router.post("/tables/create", **asdict(TableOutputPost()))
    def add_table(self,
                  table: TableInterfacePost = Depends()
                  ) -> JSONResponse:
        """
        Adds new table into db.
        Only available to admins.
        """
        table = self.table_operation.add_obj(table.data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": get_text('post').format(
                self.table_operation.model_name, table.id)}
        )
