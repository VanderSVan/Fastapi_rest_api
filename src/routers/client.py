from fastapi import Depends, Query, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from ..schemas.client.base_schemas import (ClientGetSchema,
                                           ClientPatchSchema,
                                           ClientPostSchema)
from ..schemas.client.response_schemas import (ClientResponsePatchSchema,
                                               ClientResponseDeleteSchema,
                                               ClientResponsePostSchema)
from ..crud_operations.client import ClientOperation
from ..utils.dependencies import get_db
from ..utils.responses.main import get_text

# Unfortunately prefix in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['client'])


@cbv(router)
class Client:
    db: Session = Depends(get_db)

    def __init__(self):
        self.client_operation = ClientOperation(db=self.db)

    @router.get("/clients/", response_model=list[ClientGetSchema], status_code=status.HTTP_200_OK)
    def get_all_clients(self, phone: str = Query(default=None,
                                                 description="Phone number")):
        return self.client_operation.find_all_by_params(phone=phone)

    @router.get("/clients/{client_id}", response_model=ClientGetSchema, status_code=status.HTTP_200_OK)
    def get_client(self, client_id: int = Path(..., ge=1)):
        return self.client_operation.find_by_id_or_404(client_id)

    @router.patch("/clients/{client_id}", response_model=ClientResponsePatchSchema, status_code=status.HTTP_200_OK)
    def patch_client(self, client: ClientPatchSchema, client_id: int = Path(..., ge=1)):
        self.client_operation.update_model(client_id, client)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('patch').format(
                                self.client_operation.response_elem_name, client_id
                            )})

    @router.delete("/clients/{client_id}", response_model=ClientResponseDeleteSchema, status_code=status.HTTP_200_OK)
    def delete_client(self, client_id: int):
        self.client_operation.delete_model(client_id)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('delete').format(
                                self.client_operation.response_elem_name, client_id
                            )})

    @router.post("/clients/create", response_model=ClientResponsePostSchema, status_code=status.HTTP_201_CREATED)
    def add_client(self, client: ClientPostSchema):
        client = self.client_operation.add_model(client)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": get_text('post').format(
                                self.client_operation.response_elem_name, client.id
                            )})
