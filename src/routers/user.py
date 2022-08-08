from dataclasses import asdict

from fastapi import Depends, Query, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.models.user import UserModel
from src.crud_operations.user import UserOperation
from src.swagger.user import (
    UserInterfaceGetAll,
    UserInterfacePatch,
    UserInterfacePost,

    UserOutputGetAll,
    UserOutputGet,
    UserOutputDelete,
    UserOutputPatch,
    UserOutputPost
)
from src.utils.dependencies.db import get_db
from src.utils.dependencies.auth import get_current_admin_or_superuser
from src.utils.responses.main import get_text

# Unfortunately attribute 'prefix' in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['user'])


@cbv(router)
class User:
    db: Session = Depends(get_db)
    admin_or_superuser: UserModel = Depends(get_current_admin_or_superuser)

    def __init__(self):
        self.user_operation = UserOperation(db=self.db)

    @router.get("/users/", **asdict(UserOutputGetAll()))
    def get_all_users(self,
                      user: UserInterfaceGetAll = Depends(UserInterfaceGetAll)
                      ) -> list[UserModel] | list[None]:
        """
        Returns all users from db by parameters.
        Only available to admins.
        """
        return self.user_operation.find_all_by_params(phone=user.phone, status=user.status)

    @router.get("/users/{user_id}", **asdict(UserOutputGet()))
    def get_user(self, user_id: int = Path(..., ge=1)) -> UserModel | None:
        """
        Returns one user from db by user id.
        Only available to admins.
        """
        return self.user_operation.find_by_id(user_id)

    @router.delete("/users/{user_id}", **asdict(UserOutputDelete()))
    def delete_user(self, user_id: int = Path(..., ge=1)) -> JSONResponse:
        """
         Deletes user from db by user id.
         Only available to admins.
         """
        self.user_operation.delete_obj(user_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('delete').format(
                self.user_operation.response_elem_name, user_id)}
        )

    @router.patch("/users/{user_id}", **asdict(UserOutputPatch()))
    def patch_user(self,
                   user: UserInterfacePatch = Depends(UserInterfacePatch)
                   ) -> JSONResponse:
        """
        Updates user data.
        Only available to admins.
        """
        self.user_operation.update_obj(user.user_id, user.data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('patch').format(
                self.user_operation.response_elem_name, user.user_id)}
        )

    @router.post("/users/create", **asdict(UserOutputPost()))
    def add_user(self, user: UserInterfacePost = Depends(UserInterfacePost)) -> JSONResponse:
        """
        Adds new user into db.
        Only available to admins.
        """
        user = self.user_operation.add_obj(user.data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": get_text('post').format(
                self.user_operation.response_elem_name, user.id)}
        )
