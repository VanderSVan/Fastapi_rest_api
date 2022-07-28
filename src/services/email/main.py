from pathlib import Path

from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig,
)

from src.config import Settings
from src.services.email.utils import create_expire

email_config = ConnectionConfig(
    MAIL_USERNAME=Settings.MAIL_USERNAME,
    MAIL_PASSWORD=Settings.MAIL_PASSWORD,
    MAIL_FROM=Settings.MAIL_FROM,
    MAIL_PORT=Settings.MAIL_PORT,
    MAIL_SERVER=Settings.MAIL_SERVER,
    MAIL_FROM_NAME=Settings.MAIL_FROM_NAME,
    MAIL_TLS=Settings.MAIL_TLS,
    MAIL_SSL=Settings.MAIL_SSL,
    USE_CREDENTIALS=Settings.USE_CREDENTIALS,
    VALIDATE_CERTS=Settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


def send_confirm_email(email: str,
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


def send_reset_password_email(email: str,
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
