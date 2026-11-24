from typing import Callable

from core.models import Message, Participant

Sender = Callable[[Participant, Message], None]
