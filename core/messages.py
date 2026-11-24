from core.models import Message, Pairing


def build_message(pairing: Pairing) -> Message:
    return Message(
        subject="Your Secret Santa assignment",
        body=(
            f"Hi {pairing.giver.name},\n\n"
            f"You're the Secret Santa for {pairing.giftee.name}!\n"
        ),
    )
