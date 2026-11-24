import csv
from pathlib import Path

from core.models import Participant

PARTICIPANTS_FILE = Path(__file__).parent / "participants.csv"


def load_participants(path: Path = PARTICIPANTS_FILE) -> list[Participant]:
    """Read saved participants. Returns an empty list if nothing has been saved yet."""
    if not path.exists():
        return []
    # utf-8-sig handles the hidden marker Excel adds if someone edits and saves the file there
    with path.open(newline="", encoding="utf-8-sig") as f:
        people = []
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            email = (row.get("email") or "").strip()
            if name and email:  # skip blank or incomplete rows
                people.append(Participant(name, email))
        return people


def save_participants(people: list[Participant], path: Path = PARTICIPANTS_FILE) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email"])
        for p in people:
            writer.writerow([p.name, p.email])
