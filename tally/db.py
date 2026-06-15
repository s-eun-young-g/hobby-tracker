"""SQLite store: one entry table for every hobby, plus paper categories.

The schema is migrated in place on startup (new columns are added if missing), so
existing logs are preserved. Hobby-specific values live in a JSON ``data`` column.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Optional

from .hobbies import SEED_PAPER_CATEGORIES

SCHEMA = """
CREATE TABLE IF NOT EXISTS entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hobby TEXT NOT NULL,
    title TEXT,
    date TEXT NOT NULL,
    score REAL,
    rating INTEGER,
    result TEXT,
    image_url TEXT,
    image_path TEXT,
    link TEXT,
    notes TEXT,
    data TEXT,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entry_hobby_date ON entry (hobby, date);
CREATE TABLE IF NOT EXISTS category (name TEXT PRIMARY KEY);
"""

# columns that may be missing on an older database
_MIGRATIONS = {"image_path": "ALTER TABLE entry ADD COLUMN image_path TEXT",
               "data": "ALTER TABLE entry ADD COLUMN data TEXT"}


class DB:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self._migrate()
        self._seed_categories()
        self.conn.commit()

    def _migrate(self) -> None:
        cols = {r["name"] for r in self.conn.execute("PRAGMA table_info(entry)")}
        for col, ddl in _MIGRATIONS.items():
            if col not in cols:
                self.conn.execute(ddl)

    def _seed_categories(self) -> None:
        if not self.conn.execute("SELECT 1 FROM category LIMIT 1").fetchone():
            self.conn.executemany("INSERT OR IGNORE INTO category (name) VALUES (?)",
                                  [(c,) for c in SEED_PAPER_CATEGORIES])

    # -- entries -----------------------------------------------------------
    def save(self, *, entry_id: Optional[int] = None, hobby: str, title: Optional[str],
             date: str, score: Optional[float], rating: Optional[int],
             link: Optional[str], image_url: Optional[str], image_path: Optional[str],
             data: dict, notes: Optional[str] = None) -> int:
        payload = (hobby, title, date, score, rating, None, image_url, image_path,
                   link, notes, json.dumps(data or {}))
        if entry_id is None:
            cur = self.conn.execute(
                "INSERT INTO entry (hobby, title, date, score, rating, result, image_url, "
                "image_path, link, notes, data, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (*payload, time.time()))
            self.conn.commit()
            return cur.lastrowid
        # update: keep existing image_path if no new one was provided
        if image_path is None:
            row = self.conn.execute("SELECT image_path FROM entry WHERE id=?",
                                    (entry_id,)).fetchone()
            image_path = row["image_path"] if row else None
            payload = (hobby, title, date, score, rating, None, image_url, image_path,
                       link, notes, json.dumps(data or {}))
        self.conn.execute(
            "UPDATE entry SET hobby=?, title=?, date=?, score=?, rating=?, result=?, "
            "image_url=?, image_path=?, link=?, notes=?, data=? WHERE id=?",
            (*payload, entry_id))
        self.conn.commit()
        return entry_id

    def delete(self, entry_id: int) -> None:
        self.conn.execute("DELETE FROM entry WHERE id=?", (entry_id,))
        self.conn.commit()

    def _row(self, r: sqlite3.Row) -> dict:
        d = dict(r)
        d["data"] = json.loads(d["data"]) if d.get("data") else {}
        return d

    def get(self, entry_id: int) -> Optional[dict]:
        r = self.conn.execute("SELECT * FROM entry WHERE id=?", (entry_id,)).fetchone()
        return self._row(r) if r else None

    def entries(self, hobby: Optional[str] = None, limit: Optional[int] = None) -> list[dict]:
        q = "SELECT * FROM entry"
        args: list = []
        if hobby:
            q += " WHERE hobby=?"
            args.append(hobby)
        q += " ORDER BY date DESC, id DESC"
        if limit:
            q += f" LIMIT {int(limit)}"
        return [self._row(r) for r in self.conn.execute(q, args)]

    def dates_for(self, hobby: str) -> list[str]:
        return [r["date"] for r in self.conn.execute(
            "SELECT date FROM entry WHERE hobby=?", (hobby,))]

    # -- categories --------------------------------------------------------
    def categories(self) -> list[str]:
        return [r["name"] for r in self.conn.execute(
            "SELECT name FROM category ORDER BY name")]

    def add_category(self, name: str) -> None:
        name = (name or "").strip()
        if name:
            self.conn.execute("INSERT OR IGNORE INTO category (name) VALUES (?)", (name,))
            self.conn.commit()
