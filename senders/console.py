from core.models import Message, Participant


def print_sender(to: Participant, message: Message) -> None:
    print(f"To: {to.name} <{to.email}>")
    print(f"Subject: {message.subject}")
    print(message.body)
    print("-" * 40)
