import smtplib
from email.message import EmailMessage
from uuid import uuid4

from app.core.config import settings


def send_email_via_smtp(
    to_email: str,
    subject: str,
    body: str,
) -> str:
    msg = EmailMessage()
    msg["From"] = settings.smtp_from_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)

    # SMTP does not always return a provider message id in a portable way.
    # Generate a local delivery reference for traceability.
    return f"smtp-{uuid4()}"
    