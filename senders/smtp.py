from collections.abc import Generator
from contextlib import contextmanager
from email.mime.text import MIMEText
import smtplib
import ssl

from core.models import Message, Participant
from senders import Sender


@contextmanager
def connect_email(server: str, port: int, username: str, password: str) -> Generator[Sender]:
    with smtplib.SMTP(server, port) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(username, password)

        def send(to: Participant, message: Message) -> None:
            mime = MIMEText(message.body, "plain")
            mime["Subject"] = message.subject
            mime["From"] = username
            mime["To"] = to.email
            smtp.sendmail(username, to.email, mime.as_string())

        yield send
