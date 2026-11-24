import random

from core.models import Pairing, Participant


def assign(people: list[Participant]) -> list[Pairing]:
    if len(people) < 3:
        raise ValueError("Need at least 3 participants")
    if len({p.name.strip().lower() for p in people}) != len(people):
        raise ValueError("Duplicate names")
    if len({p.email.strip().lower() for p in people}) != len(people):
        raise ValueError("Duplicate emails")
    shuffled = people[:]
    random.shuffle(shuffled)
    return [Pairing(shuffled[i], shuffled[(i + 1) % len(shuffled)]) for i in range(len(shuffled))]
