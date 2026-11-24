from contextlib import nullcontext

from dotenv import load_dotenv

from gui import Connect, SecretSantaApp
from senders.console import print_sender
from senders.smtp import connect_email

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER = "email"  # "print" or "email"

# Each takes (sending email, password) from the GUI's fields.
SENDERS: dict[str, Connect] = {
    "print": lambda user, password: nullcontext(print_sender),
    "email": lambda user, password: connect_email(SMTP_SERVER, SMTP_PORT, user, password),
}


if __name__ == "__main__":
    load_dotenv()
    SecretSantaApp(connect=SENDERS[SENDER]).mainloop()
