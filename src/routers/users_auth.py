from datetime import timedelta as td

from fastapi import Depends, Query, Path, BackgroundTasks, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
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
from ..schemes.jwt.response_schemes import Token

from ..crud_operations.user import UserOperation
from ..utils.dependencies.db import get_db
from ..utils.dependencies.auth import get_current_confirmed_user
from ..utils.responses.main import get_text
from ..utils.auth_utils.signature import Signer
from ..utils.auth_utils.jwt import JWT
from ..config import Settings
from ..services.email.main import send_confirm_email
from ..crud_operations.user_auth import UserAuthOperation

# Unfortunately attribute 'prefix' in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['user auth'])


@cbv(router)
class UserAuth:
    db: Session = Depends(get_db)

    def __init__(self):
        self.user_operation = UserAuthOperation(db=self.db)

    ###############################################################
    @router.post("/users/auth/register",
                 response_model=UserGetSchema,
                 status_code=status.HTTP_201_CREATED)
    def register_user(self,
                      user: UserPostSchema,
                      background_tasks: BackgroundTasks
                      ) -> UserModel:
        # 1. Add new user into db.
        new_user_obj: UserModel = self.user_operation.add_obj(user)

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

    ###############################################################
    @router.post("/token", response_model=Token, summary='User registration')
    def login_to_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()):
        user = self.user_operation.authenticate_user(form_data.username, form_data.password)
        access_token_expires = td(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = JWT.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    ###############################################################
    @router.get('/users/auth/me/')
    def get_current_user(self,
                         current_confirmed_user: UserModel = Depends(get_current_confirmed_user)
                         ):
        return current_confirmed_user

    ###############################################################
    @router.get('/users/auth/confirm-email/{sign}/')
    def confirm_email(self, sign: str):
        """Bla"""
        decoded_user_data: dict = Signer.unsign_object(obj=sign)
        username: str = decoded_user_data.get('username')
        self.user_operation.confirm_user_email(username)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": get_text('email_confirmed')})

    ###############################################################
    @router.get('/users/auth/{username}/reset-password/')
    def reset_password(self,
                       username: str,
                       current_confirmed_user: UserModel = Depends(get_current_confirmed_user)
                       ):
        pass
