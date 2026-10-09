import json
import random
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> list[dict]:
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


QUESTIONS = _load("questions.json")
WORDS = _load("words.json")


def categories() -> list[str]:
    return sorted({q["category"] for q in QUESTIONS})


def get_question(level: str, category: str | None = None) -> dict | None:
    pool = [
        q
        for q in QUESTIONS
        if q["level"] == level and (category is None or q["category"] == category)
    ]
    return random.choice(pool) if pool else None


def word_of_the_day() -> dict:
    idx = datetime.now(timezone.utc).timetuple().tm_yday % len(WORDS)
    return WORDS[idx]
