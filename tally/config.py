"""Runtime configuration (override with TALLY_* env vars)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(os.environ.get("TALLY_DATA_DIR", Path.home() / ".local" / "share" / "tally"))


@dataclass(frozen=True)
class Settings:
    data_dir: Path = DATA_DIR
    host: str = os.environ.get("TALLY_HOST", "0.0.0.0")
    port: int = int(os.environ.get("TALLY_PORT", "8000"))

    @property
    def db_path(self) -> Path:
        return self.data_dir / "tally.db"


settings = Settings()
