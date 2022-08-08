from pathlib import Path
from functools import lru_cache

from pydantic import BaseSettings, Field

# Paths:
api_dir = Path(__file__).parent
project_dir = api_dir.parent


class Settings(BaseSettings):
    # Database:
    PG_SUPER_DB: str = Field(..., env='PG_SUPER_DB')
    PG_SUPER_USER: str = Field(..., env='PG_SUPER_USER')
    PG_SUPER_PASSWORD: str = Field(..., env='PG_SUPER_PASSWORD')
    PG_HOST: str = Field(..., env='PG_HOST')
    PG_PORT: str = Field(..., env='PG_PORT')
    PG_USER_DB: str = Field(..., env='PG_USER_DB')
    PG_USER: str = Field(..., env='PG_USER')
    PG_USER_PASSWORD: str = Field(..., env='PG_USER_PASSWORD')
    PG_ROLE: str = Field(None, env='PG_ROLE')
    URL_EXPIRE_HOURS = 2

    # Database for tests:
    TEST_DATABASE: dict = {
        'role_name': 'test_role',
        'username': 'test_user',
        'user_password': '1111',
        'db_name': 'test_db'
    }

    # Security:
    # To generate a secure random secret key use the command in your terminal:
    # `openssl rand -hex 32`.
    SECRET_KEY: str = "Really_strong_security_key_you_really_need_to_change_it"
    ALGORITHM: str = "HS256"
    TIME_ZONE: str = 'Europe/Moscow'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    # Configuration of sending emails:
    FRONT_URL: str = 'http://127.0.0.1:8000'
    CONFIRM_EMAIL_URL: str = 'http://127.0.0.1:8000/confirm-email/{}/'
    RESET_PASSWORD_URL: str = 'http://127.0.0.1:8000/reset-password/{}/'
    MAIL_USERNAME: str = Field(..., env='MAIL_USERNAME')
    MAIL_PASSWORD: str = Field(..., env='MAIL_PASSWORD')
    MAIL_FROM: str = Field(..., env='MAIL_FROM')
    MAIL_PORT: int = Field(..., env='MAIL_PORT')
    MAIL_SERVER: str = Field(..., env='MAIL_SERVER')
    MAIL_FROM_NAME: str = Field(..., env='MAIL_FROM_NAME')
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    class Config:
        env_file = api_dir.joinpath(".env")
        env_file_encoding = 'utf-8'

    def get_database_url(self) -> str:
        """
        Gets the full path to the database.
        :return: URL string.
        """
        url: str = (
            f'postgresql+psycopg2://'
            f'{self.PG_USER}:'
            f'{self.PG_USER_PASSWORD}@'
            f'{self.PG_HOST}:'
            f'{self.PG_PORT}/'
            f'{self.PG_USER_DB}'
        )
        return url

    def get_test_database_url(self) -> str:
        """
        Gets the full path to the test database.
        :return: URL string.
        """
        url: str = (
            f"postgresql+psycopg2://"
            f"{self.TEST_DATABASE['username']}:"
            f"{self.TEST_DATABASE['user_password']}@"
            f"{self.PG_HOST}:"
            f"{self.PG_PORT}/"
            f"{self.TEST_DATABASE['db_name']}"
        )
        return url


@lru_cache()
def get_settings() -> Settings:
    """Gets cached settings."""
    return Settings()