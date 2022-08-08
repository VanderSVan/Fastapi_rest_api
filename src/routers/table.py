from dataclasses import asdict

from fastapi import Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.models.user import UserModel
from src.models.table import TableModel
from src.schemes.relationships.orders_tables import (ClientTableGetSchema,
                                                     AdminTableGetSchema)
from src.crud_operations.table import TableOperation
from src.swagger.table import (
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
from src.utils.dependencies.db import get_db
from src.utils.dependencies.auth import get_current_confirmed_user
from src.utils.responses.main import get_text

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
                       table: TableInterfaceGetAll = Depends(TableInterfaceGetAll)
                       ) -> list[TableModel] | list[None]:
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
            price_per_hour=table.price_per_hour
        )
        if not self.table_operation.check_user_access():
            result = [ClientTableGetSchema.from_orm(table_obj) for table_obj in table_objs]
        else:
            result = [AdminTableGetSchema.from_orm(table_obj) for table_obj in table_objs]

        return result

    @router.get("/tables/{table_id}", **asdict(TableOutputGet()))
    def get_table(self, table_id: int = Path(..., ge=1)) -> TableModel | None:
        """
        Returns one table from db by table id.
        Available to all confirmed users.
        Non-superuser behavior:
        Instead of a nested full order data,
        it will only return the start and end datetime.
        """
        table_obj: TableModel = self.table_operation.find_by_id_or_404(table_id)

        if not self.table_operation.check_user_access():
            result = ClientTableGetSchema.from_orm(table_obj)
        else:
            result = AdminTableGetSchema.from_orm(table_obj)

        return result

    @router.delete("/tables/{table_id}", **asdict(TableOutputDelete()))
    def delete_table(self,
                     table: TableInterfaceDelete = Depends(TableInterfaceDelete)
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
                    table: TableInterfacePatch = Depends(TableInterfacePatch)
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
                  table: TableInterfacePost = Depends(TableInterfacePost)
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
