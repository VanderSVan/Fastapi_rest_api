from fastapi import Depends, status
from sqlalchemy.orm import Session

from ..models.user import UserModel
from ..schemes.user.base_schemes import UserPatchSchema
from ..crud_operations.user import UserOperation
from ..utils.dependencies import get_db
from ..utils.exceptions import JSONException
from ..utils.responses.main import get_text


class AuthLogic:
    db: Session = Depends(get_db)

    def __init__(self):
        self.user_operation = UserOperation(db=self.db)

    """
    Класс логики авторизации, идентификации и аутентификации.
    """

    def confirm_user_email(self, user: dict):
        username: str = user.get('username')
        user: UserModel = self.user_operation.find_by_param_or_404('username', username)
        if user.status == 'confirmed':
            raise JSONException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=get_text('email_already_confirmed').format(user.username)
            )

        self.user_operation.update_model(user.id, )

# if __name__ == '__main__':
#     AuthLogic.confirm_user_email()
