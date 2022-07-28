from passlib.context import CryptContext
from passlib.exc import UnknownHashError

PASSWORD_CONTEXT = CryptContext(schemes='bcrypt')


class PasswordCryptographer:
    """Encrypts and decrypts password"""

    @staticmethod
    def bcrypt(password: str) -> str:
        """
        Encrypts password.
        :param password: User password.
        :return: Encrypted password as string.
        """

        return PASSWORD_CONTEXT.hash(password)

    @staticmethod
    def verify(hashed_password: str, input_password: str) -> bool:
        """
        Decrypts and checks the user’s password.
        :param hashed_password: User password from the db.
        :param input_password: The password entered by the user.
        :return: bool
        """

        try:
            result = PASSWORD_CONTEXT.verify(
                input_password,
                hashed_password,
            )
        except UnknownHashError:
            result = False
        return result


if __name__ == '__main__':
    # Demonstration of work:
    input_password: str = 'simple_password'
    hashed: str = PasswordCryptographer.bcrypt(input_password)
    verified: bool = PasswordCryptographer.verify(hashed, input_password)
    print(f"{input_password=}\n"
          f"{hashed=}\n"
          f"length={len(hashed)}\n"
          f"Is the password a match: {verified}")

