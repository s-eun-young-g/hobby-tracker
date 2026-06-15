"""Hobby definitions: the one place to add or change what tally tracks.

Each hobby declares its category, whether it is a daily habit (so it gets a streak),
the direction of its score (higher or lower is better, or no score), and which fields
its entry form shows. The web views and stats read these flags generically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Hobby:
    key: str
    label: str
    category: str               # "game" | "media" | "reading" | "paper"
    daily: bool                 # daily habit -> tracked as a streak
    color: str                  # gallery score-card color
    score_label: Optional[str] = None     # e.g. "points", "seconds"; None = no score
    score_better: Optional[str] = None    # "high" | "low" | None
    has_rating: bool = False
    has_result: bool = False    # win/loss vs a friend
    has_image: bool = False     # cover/poster URL


HOBBIES: dict[str, Hobby] = {
    "quartiles": Hobby("quartiles", "Quartiles", "game", True, "#6d6af5",
                       score_label="points", score_better="high"),
    "crossword": Hobby("crossword", "Crossword", "game", True, "#2aa775",
                       score_label="seconds", score_better="low"),
    "anagrams": Hobby("anagrams", "Anagrams", "game", False, "#e0883b",
                      score_label="points", score_better="high", has_result=True),
    "word_hunt": Hobby("word_hunt", "Word Hunt", "game", False, "#d6553b",
                       score_label="points", score_better="high", has_result=True),
    "set": Hobby("set", "Set", "game", False, "#9b59b6",
                 score_label="points", score_better="high", has_result=True),
    "book": Hobby("book", "Book", "reading", False, "#3b78d6",
                  has_rating=True, has_image=True),
    "movie": Hobby("movie", "Movie", "media", False, "#c0392b",
                   has_rating=True, has_image=True),
    "paper": Hobby("paper", "Paper", "paper", False, "#16808a", has_image=False),
}

ORDER = list(HOBBIES.keys())


def get(key: str) -> Optional[Hobby]:
    return HOBBIES.get(key)


def daily_hobbies() -> list[Hobby]:
    return [h for h in HOBBIES.values() if h.daily]
