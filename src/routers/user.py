from fastapi import Depends, Query, Path, BackgroundTasks, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from ..models.user import UserModel
from ..schemes.user.base_schemes import (UserGetSchema,
                                         UserPatchSchema,
                                         UserPostSchema)
from ..schemes.user.response_schemes import (UserResponsePatchSchema,
                                             UserResponseDeleteSchema,
                                             UserResponsePostSchema)

from ..crud_operations.user import UserOperation
from ..utils.dependencies import get_db
from ..utils.responses.main import get_text
from ..utils.auth_utils.signature import Signer
from ..config import Settings
from ..services.email.main import send_confirm_email

# Unfortunately attribute 'prefix' in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['user'])
auth_router = InferringRouter(tags=['user auth'])


@cbv(router)
class User:
    db: Session = Depends(get_db)

    def __init__(self):
        self.user_operation = UserOperation(db=self.db)

    @router.get("/users/", response_model=list[UserGetSchema], status_code=status.HTTP_200_OK)
    def get_all_users(self, phone: str = Query(default=None,
                                               description="Phone number")):
        return self.user_operation.find_all_by_params(phone=phone)

    @router.get("/users/{user_id}", response_model=UserGetSchema, status_code=status.HTTP_200_OK)
    def get_user(self, user_id: int = Path(..., ge=1)):
        return self.user_operation.find_by_id_or_404(user_id)

    @router.patch("/users/{user_id}", response_model=UserResponsePatchSchema, status_code=status.HTTP_200_OK)
    def patch_user(self, user: UserPatchSchema, user_id: int = Path(..., ge=1)):
        self.user_operation.update_model(user_id, user)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('patch').format(
                                self.user_operation.response_elem_name, user_id
                            )})

    @router.delete("/users/{user_id}", response_model=UserResponseDeleteSchema, status_code=status.HTTP_200_OK)
    def delete_user(self, user_id: int):
        self.user_operation.delete_model(user_id)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('delete').format(
                                self.user_operation.response_elem_name, user_id
                            )})

    @router.post("/users/create", response_model=UserResponsePostSchema, status_code=status.HTTP_201_CREATED)
    def add_user(self, user: UserPostSchema):
        user = self.user_operation.add_model(user)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": get_text('post').format(
                                self.user_operation.response_elem_name, user.id
                            )})


@cbv(auth_router)
class UserAuth:
    db: Session = Depends(get_db)

    def __init__(self):
        self.user_operation = UserOperation(db=self.db)

    @auth_router.post("/users/register",
                      response_model=UserGetSchema,
                      status_code=status.HTTP_201_CREATED)
    def register_user(self,
                      user: UserPostSchema,
                      background_tasks: BackgroundTasks) -> UserModel:
        # 1. Add new user into db.
        new_user_obj: UserModel = self.user_operation.add_model(user)

        # 2. Encode the username and pasting it into the url
        encoded_user_data: str = Signer.sign_object({'username': user.username})
        url_confirming_page: str = Settings.CONFIRM_EMAIL_URL.format(encoded_user_data)

        # 3. Composing a letter to send. Letter to confirm registration.
        email, params = send_confirm_email(email=user.email, url=url_confirming_page)
        message, template_name = params

        # 4. Start sending letter to email with background task.
        background_tasks.add_task(email.send_message,
                                  message=message,
                                  template_name=template_name,
                                  )
        return new_user_obj

    @auth_router.get('/confirm-email/{sign}/')
    def confirm_email(self, sign: str):
        """Bla"""
        decoded_user_data: dict = Signer.unsign_object(obj=sign)
        username: str = decoded_user_data.get('username')
        self.user_operation.confirm_user_email(username)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('email_confirmed')})
