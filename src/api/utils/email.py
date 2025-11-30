import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List, Optional, Dict, Union

# Load config from environment
# Defaults are placeholders. Production must set these env vars.
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "apikey"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "secret"),
    MAIL_FROM = os.getenv("MAIL_FROM", "noreply@auditflow.com"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.sendgrid.net"),
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True").lower() == "true",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_email(
    recipients: List[EmailStr],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html,
    attachments: Optional[List[Union[Dict, str]]] = None
):
    """
    Sends an email using fastapi-mail.

    :param recipients: List of email addresses
    :param subject: Email subject
    :param body: Email body (HTML or Text)
    :param subtype: MessageType.html or MessageType.plain
    :param attachments: List of file paths or Dicts like {'file': bytes, 'filename': str, 'mime_type': str}
    """

    # Check if email is disabled or mock mode
    if os.getenv("MOCK_EMAIL", "false").lower() == "true":
        print(f"[MOCK EMAIL] To: {recipients} | Subject: {subject}")
        return

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=subtype,
        attachments=attachments
    )

    fm = FastMail(conf)
    await fm.send_message(message)
