"""SQLite store: a single entry table for every hobby."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hobby TEXT NOT NULL,
    title TEXT,
    date TEXT NOT NULL,           -- YYYY-MM-DD
    score REAL,
    rating INTEGER,              -- 1..5
    result TEXT,                 -- win / loss / draw
    image_url TEXT,
    link TEXT,
    notes TEXT,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entry_hobby_date ON entry (hobby, date);
"""


class DB:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def add(self, hobby: str, date: str, *, title: Optional[str] = None,
            score: Optional[float] = None, rating: Optional[int] = None,
            result: Optional[str] = None, image_url: Optional[str] = None,
            link: Optional[str] = None, notes: Optional[str] = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO entry (hobby, title, date, score, rating, result, image_url, "
            "link, notes, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (hobby, title, date, score, rating, result, image_url, link, notes, time.time()),
        )
        self.conn.commit()
        return cur.lastrowid

    def delete(self, entry_id: int) -> None:
        self.conn.execute("DELETE FROM entry WHERE id=?", (entry_id,))
        self.conn.commit()

    def entries(self, hobby: Optional[str] = None, limit: Optional[int] = None) -> list[dict]:
        q = "SELECT * FROM entry"
        args: list = []
        if hobby:
            q += " WHERE hobby=?"
            args.append(hobby)
        q += " ORDER BY date DESC, id DESC"
        if limit:
            q += f" LIMIT {int(limit)}"
        return [dict(r) for r in self.conn.execute(q, args)]

    def dates_for(self, hobby: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT date FROM entry WHERE hobby=? ORDER BY date", (hobby,))
        return [r["date"] for r in rows]

    def logged_on(self, hobby: str, date: str) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM entry WHERE hobby=? AND date=? LIMIT 1", (hobby, date)
        ).fetchone() is not None
