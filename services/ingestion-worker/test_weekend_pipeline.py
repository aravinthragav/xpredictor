"""
services/ingestion-worker/test_weekend_pipeline.py
Unit & Integration Tests for the 2-Step Architecture:
Step 1: Weekday Live Buffer
Step 2: Weekend Batch Ingestion Pipeline
"""

import os
import sys
import time
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kronos-embedder")))

from live_buffer import LiveMarketBuffer
from weekend_batch import WeekendBatchEngine


@pytest.fixture
def temp_db(tmp_path):
    db_file = str(tmp_path / "test_buffer.db")
    return db_file


def test_live_buffer_crud(temp_db):
    buf = LiveMarketBuffer(db_path=temp_db)
    
    # 1. Insert a single bar
    inserted = buf.record_bar("XAUUSD", "1h", 1700000000, 4150.0, 4155.0, 4148.0, 4153.0, 500.0)
    assert inserted is True
    
    # Duplicate insertion should be ignored
    inserted_dup = buf.record_bar("XAUUSD", "1h", 1700000000, 4150.0, 4155.0, 4148.0, 4153.0, 500.0)
    assert inserted_dup is True # Handled gracefully via INSERT OR IGNORE

    stats = buf.get_stats()
    assert stats["total_buffered_bars"] == 1
    assert stats["unindexed_bars"] == 1

    # 2. Batch insert 100 bars
    bars = []
    base_ts = 1700003600
    for i in range(100):
        bars.append({
            "symbol": "XAUUSD",
            "timeframe": "1h",
            "timestamp": base_ts + i * 3600,
            "open": 4150.0 + i,
            "high": 4155.0 + i,
            "low": 4148.0 + i,
            "close": 4153.0 + i,
            "volume": 600.0
        })
    count = buf.batch_record_bars(bars)
    assert count == 100

    unindexed = buf.get_unindexed_bars("XAUUSD", "1h")
    assert len(unindexed) == 101

    # 3. Mark first 50 as indexed
    ids_to_mark = [b["id"] for b in unindexed[:50]]
    marked = buf.mark_bars_indexed(ids_to_mark)
    assert marked == 50

    remaining = buf.get_unindexed_bars("XAUUSD", "1h")
    assert len(remaining) == 51


def test_weekend_batch_execution(temp_db, monkeypatch):
    buf = LiveMarketBuffer(db_path=temp_db)
    
    # Populate buffer with 120 bars (sufficient for L=64 + 20 forward bars)
    base_ts = 1710000000
    bars = []
    p = 4120.0
    for i in range(120):
        p += (np.sin(i * 0.15) + (i % 2 - 0.5)) * 1.5
        bars.append({
            "symbol": "XAUUSD",
            "timeframe": "1h",
            "timestamp": base_ts + i * 3600,
            "open": p - 0.8,
            "high": p + 1.6,
            "low": p - 1.2,
            "close": p + 0.5,
            "volume": 850.0
        })
    buf.batch_record_bars(bars)

    # Instantiate engine with custom buffer
    engine = WeekendBatchEngine(window_length=64, stride=4)
    engine.buffer = buf

    res = engine.run_sync(symbol="XAUUSD", timeframe="1h", dry_run=False)

    assert res["status"] == "success"
    assert res["windows_indexed"] > 0
    assert os.path.exists(res["output_staged_file"])

    # Ensure buffer bars are now marked as indexed
    remaining = buf.get_unindexed_bars("XAUUSD", "1h")
    assert len(remaining) == 0
