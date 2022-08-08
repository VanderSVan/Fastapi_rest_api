from datetime import timedelta as td
from dataclasses import asdict

from fastapi import Depends, BackgroundTasks, Path, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.models.user import UserModel
from src.schemes.user.base_schemes import (UserPostSchema,
                                           UserResetPasswordSchema)
from src.swagger.user_auth import (
    UserAuthOutputGetCurrentUser,
    UserAuthOutputConfirmEmail,
    UserAuthOutputResetPassword,
    UserAuthOutputGetToken,
    UserAuthOutputRegister,
    UserAuthOutputConfirmNewPassword
)
from src.utils.dependencies.db import get_db
from src.utils.dependencies.auth import get_current_confirmed_user
from src.utils.responses.main import get_text
from src.utils.auth_utils.signature import Signer
from src.utils.auth_utils.jwt import JWT
from src.config import Settings
from src.services.email.main import compose_email_with_action_link
from src.crud_operations.user_auth import UserAuthOperation

# Unfortunately attribute 'prefix' in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['user auth'])


@cbv(router)
class UserAuth:
    db: Session = Depends(get_db)

    def __init__(self):
        self.user_operation = UserAuthOperation(db=self.db)

    @router.get('/users/auth/me/', **asdict(UserAuthOutputGetCurrentUser()))
    def get_current_user(self,
                         current_confirmed_user: UserModel = Depends(get_current_confirmed_user)
                         ) -> UserModel:
        """Returns current user data."""
        return current_confirmed_user

    @router.get('/users/auth/confirm-email/{sign}/', **asdict(UserAuthOutputConfirmEmail()))
    def confirm_email(self, sign: str = Path(...)):
        """
        Request to confirm the user’s email.
        :param sign: it is encoded user data, such as a username.
        """
        decoded_user_data: dict = Signer.unsign_object(obj=sign)
        username: str = decoded_user_data.get('username')
        self.user_operation.confirm_user_email(username)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('email_confirmed')}
        )

    @router.get('/users/auth/reset-password/', **asdict(UserAuthOutputResetPassword()))
    def reset_password(self,
                       background_tasks: BackgroundTasks,
                       current_confirmed_user: UserModel = Depends(get_current_confirmed_user)
                       ):
        """
        Request to reset the user’s password.
        The user must be in authenticated status else he cannot access this endpoint.
        It then sends an email to the user to reset the password.
        :param background_tasks: task that runs in the background.
        :param current_confirmed_user: user data.
        """
        # 1. Find user into db
        user: UserModel = self.user_operation.find_by_id_or_404(current_confirmed_user.id)

        # 2. Compose email with action link
        email, params = compose_email_with_action_link(username=user.username,
                                                       email=user.email,
                                                       action='reset_password',
                                                       prefix_link=Settings.RESET_PASSWORD_URL
                                                       )
        message, template_name = params

        # 3. Start sending letter to email with background task.
        background_tasks.add_task(email.send_message,
                                  message=message,
                                  template_name=template_name,
                                  )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('reset_password')}
        )

    @router.post("/token", **asdict(UserAuthOutputGetToken()))
    def create_token(self,
                     form_data: OAuth2PasswordRequestForm = Depends()
                     ) -> dict:
        """
        Gets authenticated data and returns a token if the data is valid.
        :param form_data: input data such as login and password.
        :return: {'access_token': str, 'token_type': 'bearer'}
        """
        user = self.user_operation.authenticate_user(form_data.username, form_data.password)
        access_token_expires = td(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = JWT.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @router.post("/users/auth/register", **asdict(UserAuthOutputRegister()))
    def register_user(self,
                      user: UserPostSchema,
                      background_tasks: BackgroundTasks
                      ) -> UserModel:
        """
        Gets new user data and saves it into db.
        It then sends an email to the user to confirm the password.
        :param user: user data.
        :param background_tasks: task that runs in the background.
        :return: UserModel.
        """
        # 1. Add new user into db.
        new_user_obj: UserModel = self.user_operation.add_obj(user)

        # 2. Compose email with action link
        email, params = compose_email_with_action_link(username=user.username,
                                                       email=user.email,
                                                       action='confirm_email',
                                                       prefix_link=Settings.CONFIRM_EMAIL_URL
                                                       )
        message, template_name = params

        # 3. Start sending letter to email with background task.
        background_tasks.add_task(email.send_message,
                                  message=message,
                                  template_name=template_name,
                                  )
        return new_user_obj

    @router.post('/users/auth/confirm-reset-password/{sign}/',
                 **asdict(UserAuthOutputConfirmNewPassword()))
    def confirm_reset_password(self,
                               sign: str,
                               new_password_data: UserResetPasswordSchema):
        """
        Gets the user's new password and saves it in the database.
        :param sign: it is encoded user data, such as a username.
        :param new_password_data: new password
        :return: JSONResponse
        """

        decoded_user_data: dict = Signer.unsign_object(obj=sign)
        username: str = decoded_user_data.get('username')
        self.user_operation.confirm_reset_password(username, new_password_data.password)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('changed_password')}
        )
