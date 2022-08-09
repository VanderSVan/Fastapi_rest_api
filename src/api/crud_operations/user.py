from sqlalchemy import and_

from src.api.crud_operations.base_crud_operations import ModelOperation
from src.api.models.user import UserModel
from src.api.schemes.user.base_schemes import UserPatchSchema, UserPostSchema
from src.utils.auth_utils.password_cryptograph import PasswordCryptographer


class UserOperation(ModelOperation):
    def __init__(self, db):
        self.model = UserModel
        self.patch_schema = UserPatchSchema
        self.response_elem_name = 'user'
        self.db = db

    def find_all_by_params(self, **kwargs) -> list[UserModel]:
        phone = kwargs.get('phone')
        status = kwargs.get('status')
        return (self.db
                    .query(UserModel)
                    .filter(and_(
                                 (UserModel.phone == phone
                                  if phone is not None else True),
                                 (UserModel.status == status
                                  if status is not None else True),
                                )
                            )
                    .all())

    def add_obj(self, new_user_schema: UserPostSchema) -> UserModel:
        # Find max user id.
        max_id: int = self.get_max_id()

        # Hash the password.
        hashed_password = PasswordCryptographer.bcrypt(new_user_schema.password)

        # Create new user object.
        new_user_obj: UserModel = self.model(
            id=max_id + 1,
            hashed_password=hashed_password,
            status='unconfirmed',
            **new_user_schema.dict(exclude={'password'})
        )

        # Save new user object into db.
        self.db.add(new_user_obj)
        self.db.commit()
        self.db.refresh(new_user_obj)

        return new_user_obj




