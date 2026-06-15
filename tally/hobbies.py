"""Hobby definitions and their per-hobby form fields.

Each hobby lists the fields its form shows. A field says where its value is stored:
- "title"  -> the entry title column
- "score"  -> the numeric score column (used for streaks-free bests; time is seconds)
- "rating" -> the 1-5 rating column
- "link"   -> the link/url column
- "image"  -> an uploaded image (or a pasted URL)
- "date"   -> the entry date
- "data"   -> the per-entry JSON blob (everything hobby-specific)

Add a hobby or a field by editing this file; the forms, gallery, and tracker read it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

BOOK_GENRES = ("Fiction", "Nonfiction", "Poetry", "Short story")
MOVIE_GENRES = ("Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
                "Drama", "Fantasy", "Horror", "Musical", "Mystery", "Romance",
                "Sci-Fi", "Thriller", "Western")
DIFFICULTY = ("Easy", "Moderate", "Hard", "Challenging")
SEED_PAPER_CATEGORIES = ("animals", "history", "for the lols")


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    type: str = "text"     # text,number,rating,select,time,url,date,category,image
    col: str = "data"      # title,score,rating,link,date,image,data
    options: tuple = ()
    required: bool = False
    placeholder: str = ""


@dataclass(frozen=True)
class Hobby:
    key: str
    label: str
    category: str          # game | media | reading | paper | dance
    daily: bool
    color: str
    score_better: Optional[str] = None     # high | low | None
    score_label: Optional[str] = None
    score_is_time: bool = False
    fields: tuple = ()

    @property
    def has_image(self) -> bool:
        return any(f.type == "image" for f in self.fields)


def _date() -> Field:
    return Field("date", "Date", "date", "date")


HOBBIES: dict[str, Hobby] = {
    "quartiles": Hobby(
        "quartiles", "Quartiles", "game", True, "#6d6af5",
        score_better="high", score_label="points",
        fields=(Field("score", "Score", "number", "score"), _date())),
    "crossword": Hobby(
        "crossword", "Crossword", "game", True, "#2aa775",
        score_better="low", score_label="time", score_is_time=True,
        fields=(Field("time", "Time", "time", "score"),
                Field("difficulty", "Difficulty", "select", "data", options=DIFFICULTY),
                _date())),
    "set": Hobby(
        "set", "Set", "game", False, "#9b59b6",
        score_better="low", score_label="time", score_is_time=True,
        fields=(Field("time", "Time", "time", "score"), _date())),
    "anagrams": Hobby(
        "anagrams", "Anagrams", "game", False, "#e0883b",
        score_better="high", score_label="points",
        fields=(Field("score", "Score", "number", "score"),
                Field("opponents", "Opponents", "text", "data", placeholder="who you played"),
                _date())),
    "word_hunt": Hobby(
        "word_hunt", "Word Hunt", "game", False, "#d6553b",
        score_better="high", score_label="points",
        fields=(Field("score", "Score", "number", "score"),
                Field("opponents", "Opponents", "text", "data", placeholder="who you played"),
                _date())),
    "dialed_sound": Hobby(
        "dialed_sound", "Dialed Sound", "game", False, "#0aa1dc",
        score_better="high", score_label="/ 10",
        fields=(Field("score", "Score (out of 10)", "number", "score",
                      placeholder="e.g. 7.42"),
                Field("mode", "Mode", "select", "data", options=("Daily", "Free play")),
                _date())),
    "book": Hobby(
        "book", "Book", "reading", False, "#3b78d6",
        fields=(Field("title", "Title", "text", "title", required=True),
                Field("author", "Author", "text", "data"),
                Field("rating", "Rating", "rating", "rating"),
                Field("genre", "Genre", "select", "data", options=BOOK_GENRES),
                Field("image", "Cover", "image", "image"),
                _date())),
    "movie": Hobby(
        "movie", "Movie", "media", False, "#c0392b",
        fields=(Field("title", "Title", "text", "title", required=True),
                Field("director", "Director", "text", "data"),
                Field("rating", "Rating", "rating", "rating"),
                Field("genre", "Genre", "select", "data", options=MOVIE_GENRES),
                Field("image", "Poster", "image", "image"),
                _date())),
    "paper": Hobby(
        "paper", "Paper", "paper", False, "#16808a",
        fields=(Field("title", "Title", "text", "title", placeholder="optional"),
                Field("url", "URL", "url", "link", required=True),
                Field("category", "Category", "category", "data"),
                _date())),
    "dances": Hobby(
        "dances", "Dance", "dance", False, "#e84393",
        fields=(Field("song", "Song", "text", "title", required=True,
                      placeholder="Song by Artist"),
                Field("choreographer", "Choreographer", "text", "data"),
                Field("image", "Image", "image", "image"),
                _date())),
}

ORDER = list(HOBBIES.keys())


def get(key: str) -> Optional[Hobby]:
    return HOBBIES.get(key)


def daily_hobbies() -> list[Hobby]:
    return [h for h in HOBBIES.values() if h.daily]
