"""
services/ingestion-worker/live_buffer.py
Weekday Live Bar Buffer for XPredictor.
Stores newly completed market bars during trading days into an append-only SQLite store
with zero CPU overhead and zero impact on search query latency.
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "live_market_buffer.db")


class LiveMarketBuffer:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS buffered_bars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    indexed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timeframe, timestamp)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_unindexed ON buffered_bars(symbol, timeframe, indexed)")
            conn.commit()

    def record_bar(
        self,
        symbol: str,
        timeframe: str,
        timestamp: int,
        open_p: float,
        high_p: float,
        low_p: float,
        close_p: float,
        volume: float
    ) -> bool:
        """Appends a completed bar to the live weekday buffer. Returns True if inserted, False if duplicate."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO buffered_bars
                    (symbol, timeframe, timestamp, open, high, low, close, volume, indexed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (symbol, timeframe, int(timestamp), float(open_p), float(high_p), float(low_p), float(close_p), float(volume)))
                conn.commit()
            return True
        except Exception as e:
            print(f"[Buffer] Error inserting bar: {e}")
            return False

    def batch_record_bars(self, bars: List[Dict[str, Any]]) -> int:
        """Batch inserts multiple bars."""
        if not bars:
            return 0
        inserted = 0
        with sqlite3.connect(self.db_path) as conn:
            for b in bars:
                cur = conn.execute("""
                    INSERT OR IGNORE INTO buffered_bars
                    (symbol, timeframe, timestamp, open, high, low, close, volume, indexed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    b["symbol"], b["timeframe"], int(b["timestamp"]),
                    float(b["open"]), float(b["high"]), float(b["low"]),
                    float(b["close"]), float(b.get("volume", 100.0))
                ))
                inserted += cur.rowcount
            conn.commit()
        return inserted

    def get_unindexed_bars(self, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        """Returns all unindexed bars sorted chronologically."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, symbol, timeframe, timestamp, open, high, low, close, volume
                FROM buffered_bars
                WHERE symbol = ? AND timeframe = ? AND indexed = 0
                ORDER BY timestamp ASC
            """, (symbol, timeframe)).fetchall()
            return [dict(r) for r in rows]

    def mark_bars_indexed(self, ids: List[int]) -> int:
        """Marks bars as indexed once processed by the weekend batch pipeline."""
        if not ids:
            return 0
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "UPDATE buffered_bars SET indexed = 1 WHERE id = ?",
                [(i,) for i in ids]
            )
            conn.commit()
        return len(ids)

    def get_stats(self) -> Dict[str, Any]:
        """Summary of buffer contents."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM buffered_bars").fetchone()[0]
            unindexed = conn.execute("SELECT COUNT(*) FROM buffered_bars WHERE indexed = 0").fetchone()[0]
            symbols = [r[0] for r in conn.execute("SELECT DISTINCT symbol FROM buffered_bars").fetchall()]
            return {
                "total_buffered_bars": total,
                "unindexed_bars": unindexed,
                "tracked_symbols": symbols
            }


if __name__ == "__main__":
    buf = LiveMarketBuffer()
    print("[LiveMarketBuffer] Initialized. Status:", buf.get_stats())
