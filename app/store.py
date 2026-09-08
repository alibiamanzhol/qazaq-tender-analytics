import sqlite3
from pathlib import Path
from .models import Tender

DB_PATH = Path(__file__).resolve().parent.parent / "tenders.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tenders (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    customer TEXT NOT NULL,
    supplier TEXT NOT NULL,
    budget_kzt REAL NOT NULL,
    award_kzt REAL NOT NULL,
    bids_count INTEGER NOT NULL,
    license_count INTEGER NOT NULL,
    status TEXT NOT NULL
)
"""

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def upsert_many(items: list[Tender]) -> int:
    with connect() as conn:
        for t in items:
            conn.execute(
                """INSERT INTO tenders VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                  title=excluded.title, customer=excluded.customer,
                  supplier=excluded.supplier, budget_kzt=excluded.budget_kzt,
                  award_kzt=excluded.award_kzt, bids_count=excluded.bids_count,
                  license_count=excluded.license_count, status=excluded.status""",
                (t.id, t.title, t.customer, t.supplier, t.budget_kzt,
                 t.award_kzt, t.bids_count, t.license_count, t.status),
            )
    return len(items)


def all_tenders() -> list[Tender]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM tenders ORDER BY budget_kzt DESC").fetchall()
    return [Tender(**dict(row)) for row in rows]


def get_tender(tender_id: str) -> Tender | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM tenders WHERE id=?", (tender_id,)).fetchone()
    return Tender(**dict(row)) if row else None
