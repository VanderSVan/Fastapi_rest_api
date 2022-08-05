from fastapi import Depends, Query, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.models.user import UserModel
from src.models.table import TableModel
from src.schemes.table.base_schemes import (TablePatchSchema,
                                            TablePostSchema)
from src.schemes.relationships.orders_tables import (ClientTableGetSchema,
                                                     AdminTableGetSchema)
from src.schemes.table.response_schemes import (TableResponsePatchSchema,
                                                TableResponseDeleteSchema,
                                                TableResponsePostSchema)
from src.crud_operations.table import TableOperation
from src.utils.dependencies.db import get_db
from src.utils.dependencies.auth import (get_current_admin_or_superuser,
                                         get_current_confirmed_user)
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

    ###############################################################
    @router.get("/tables/", status_code=status.HTTP_200_OK)
    def get_all_tables(self,
                       type: str = Query(default=None,
                                         description='Table type'),
                       number_of_seats: int = Query(default=None,
                                                    description='Less or equal'),
                       price_per_hour: float = Query(default=None,
                                                     description='Less or equal')
                       ):
        """
        Returns all tables from db by parameters.
        Available to all confirmed users.
        """
        table_objs: list[TableModel] = self.table_operation.find_all_by_params(type=type,
                                                                               number_of_seats=number_of_seats,
                                                                               price_per_hour=price_per_hour)
        if not self.table_operation.check_user_access():
            result = [ClientTableGetSchema.from_orm(table_obj) for table_obj in table_objs]
        else:
            result = [AdminTableGetSchema.from_orm(table_obj) for table_obj in table_objs]

        return result

    ###############################################################
    @router.get("/tables/{table_id}", status_code=status.HTTP_200_OK)
    def get_table(self,
                  table_id: int = Path(..., ge=1)
                  ):
        """
        Returns one table from db by table id.
        Available to all confirmed users.
        """
        table_obj: TableModel = self.table_operation.find_by_id_or_404(table_id)

        if not self.table_operation.check_user_access():
            result = ClientTableGetSchema.from_orm(table_obj)
        else:
            result = AdminTableGetSchema.from_orm(table_obj)

        return result

    ###############################################################
    @router.patch("/tables/{table_id}",
                  response_model=TableResponsePatchSchema,
                  status_code=status.HTTP_200_OK
                  )
    def patch_table(self,
                    new_table_data: TablePatchSchema,
                    table_id: int = Path(..., ge=1),
                    admin: UserModel = Depends(get_current_admin_or_superuser)
                    ) -> JSONResponse:
        """
        Updates table data.
        Only available to admins.
        """
        self.table_operation.update_obj(table_id, new_table_data)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('patch').format(
                                self.table_operation.model_name, table_id
                            )})

    ###############################################################
    @router.delete("/tables/{table_id}",
                   response_model=TableResponseDeleteSchema,
                   status_code=status.HTTP_200_OK
                   )
    def delete_table(self,
                     table_id: int,
                     admin: UserModel = Depends(get_current_admin_or_superuser)
                     ) -> JSONResponse:
        """
        Deletes table from db by table id.
        Only available to admins.
        """
        self.table_operation.delete_obj(table_id)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('delete').format(
                                self.table_operation.model_name, table_id
                            )})

    ###############################################################
    @router.post("/tables/create",
                 response_model=TableResponsePostSchema,
                 status_code=status.HTTP_201_CREATED
                 )
    def add_table(self,
                  table: TablePostSchema,
                  admin: UserModel = Depends(get_current_admin_or_superuser)
                  ) -> JSONResponse:
        """
        Adds new table into db.
        Only available to admins.
        """
        table = self.table_operation.add_obj(table)

        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": get_text('post').format(
                                self.table_operation.model_name, table.id
                            )})
