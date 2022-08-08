from pathlib import Path
from typing import NoReturn, Literal

from fastapi import status, BackgroundTasks
from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig,
)

from src.config import get_settings
from src.services.email.utils import create_expire
from src.utils.auth_utils.signature import Signer
from src.utils.logger.main import logger
from src.utils.exceptions import JSONException
from src.utils.responses.main import get_text

settings = get_settings()

email_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_TLS=settings.MAIL_TLS,
    MAIL_SSL=settings.MAIL_SSL,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


def compose_confirm_email(email: str,
                          url: str
                          ) -> tuple[FastMail, list[MessageSchema, str]]:
    """
    Composing a letter to send. Letter to confirm registration.
    :param email: User email.
    :param url: The URL to go to verify the email.
    :return: Tuple that contains the FastMail instance, schemas, and template name.
    """

    template_name = 'confirm_email.html'
    expire = create_expire()
    template_body = {
        'heading': 'You have registered on the service "Restaurant-API".',
        'text': (
            'You need to confirm your email address: '
        ),
        'email': email,
        'expire': expire,
        'url': url
    }
    message = MessageSchema(
        subject='Restaurant-API: registration for the service.',
        recipients=[email],
        template_body=template_body
    )

    fm = FastMail(email_config)
    params = [message, template_name]
    return fm, params


def compose_reset_password_email(email: str,
                                 url: str
                                 ) -> tuple[FastMail, list[MessageSchema, str]]:
    """
    Composing a letter to send. Letter to reset user password.
    :param email: User email.
    :param url: The URL to go to reset user password.
    :return: Tuple that contains the FastMail instance, schemas, and template name.
    """

    template_name = 'reset_password.html'
    expire = create_expire()
    template_body = {
        'heading': (
            'You requested password reset on "Restaurant-API".'
        ),
        'text': (
            'Click the link below to confirm: '
        ),
        'expire': expire,
        'url': url
    }
    message = MessageSchema(
        subject='Restaurant-API: Reset password.',
        recipients=[email],
        template_body=template_body
    )

    fm = FastMail(email_config)
    params = [message, template_name]
    return fm, params


def compose_email_with_action_link(
        username: str,
        email: str,
        action: Literal['confirm_email'] | Literal['reset_password'],
        prefix_link: str
) -> tuple[FastMail, list[MessageSchema, str]]:
    """Sends email letter that contain action link."""

    # 1. Encode the username and pasting it into the url
    encoded_user_data: str = Signer.sign_object({'username': username})
    action_link: str = prefix_link.format(encoded_user_data)

    # 2. Composing a letter to send. Letter with action link.
    match action:
        case 'confirm_email':
            email, params = compose_confirm_email(email=email, url=action_link)
        case 'reset_password':
            email, params = compose_reset_password_email(email=email, url=action_link)
        case _:
            logger.exception(
                ValueError("The 'action' argument must be 'confirm_email' or 'reset_password' only.")
            )
            raise JSONException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=get_text('err_500')
            )
    return email, params
