"""Create the small SQLite database used by the MVP."""

from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "acme_audio.db"
SCHEMA = ROOT / "data" / "seed" / "schema.sql"
SEED = ROOT / "data" / "seed" / "seed.sql"


if DATABASE.exists():
    DATABASE.unlink()

with sqlite3.connect(DATABASE) as connection:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA.read_text(encoding="utf-8"))
    connection.executescript(SEED.read_text(encoding="utf-8"))

print(f"Created {DATABASE}")
