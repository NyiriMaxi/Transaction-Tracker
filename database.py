"""
SQLite adatbázis kezelő.
"""

import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    datum     TEXT    NOT NULL,
    osszeg    REAL    NOT NULL,
    targy     TEXT    NOT NULL,
    kategoria TEXT    NOT NULL
);
"""


class TransactionDB:

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "data", "transactions.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error("Adatbázis hiba: %s", e)
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(CREATE_TABLE)
        logger.info("Adatbázis inicializálva: %s", self.db_path)

    def insert(
        self,
        datum: str,
        osszeg: float,
        targy: str,
        kategoria: str,
    ) -> int:
        """Ment egy tranzakciót. Visszaadja az új sor id-ját."""
        sql = "INSERT INTO transactions (datum, osszeg, targy, kategoria) VALUES (?, ?, ?, ?)"
        with self._conn() as conn:
            cur = conn.execute(sql, (datum, osszeg, targy, kategoria))
            row_id = cur.lastrowid
        logger.info("Mentve (#%d): %s | %.0f Ft | %s -> %s", row_id, datum, osszeg, targy, kategoria)
        return row_id

    def get_all(self) -> list[dict]:
        """Visszaadja az összes tranzakciót csökkenő dátum szerint."""
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM transactions ORDER BY datum DESC").fetchall()
        return [dict(r) for r in rows]

    def get_monthly_summary(self, year_month: str | None = None) -> dict[str, float]:
        """
        Kategóriánkénti összeg egy hónapra.
        year_month: 'YYYY-MM' (alapértelmezett: aktuális hónap)
        """
        if year_month is None:
            year_month = datetime.now().strftime("%Y-%m")
        sql = """
            SELECT kategoria, SUM(osszeg) as total
            FROM transactions
            WHERE datum LIKE ?
            GROUP BY kategoria
            ORDER BY total DESC
        """
        with self._conn() as conn:
            rows = conn.execute(sql, (f"{year_month}%",)).fetchall()
        return {r["kategoria"]: r["total"] for r in rows}

    def get_by_category(self, kategoria: str) -> list[dict]:
        """Visszaadja egy kategória összes tranzakcióját."""
        sql = "SELECT * FROM transactions WHERE kategoria = ? ORDER BY datum DESC"
        with self._conn() as conn:
            rows = conn.execute(sql, (kategoria,)).fetchall()
        return [dict(r) for r in rows]
    
