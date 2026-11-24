from dataclasses import dataclass


@dataclass(frozen=True)
class Participant:
    name: str
    email: str


@dataclass(frozen=True)
class Pairing:
    giver: Participant
    giftee: Participant


@dataclass(frozen=True)
class Message:
    subject: str
    body: str
