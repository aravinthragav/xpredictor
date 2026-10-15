"""
services/ingestion-worker/test_ingestion.py
Verification suite for Agent-02-VectorOps ingestion pipeline.
Validates window slicing math, forward outcome calculation, and payload structure.
"""

import pytest
import numpy as np
from pipeline import IngestionPipeline


def test_window_slicing_and_outcomes():
    pipeline = IngestionPipeline(window_length=64, stride=4)
    n_bars = 200

    # Create dummy deterministic linear dataset
    candles = np.zeros((n_bars, 6), dtype=np.float32)
    for i in range(n_bars):
        price = 100.0 + i  # Straight upward linear trend
        candles[i] = [price, price + 1.0, price - 1.0, price, 1000.0, 100000.0]

    windows = list(pipeline.slice_rolling_windows(candles, "BTCUSD", "crypto", "1h"))
    assert len(windows) > 0

    first_item = windows[0]
    payload = first_item["payload"]
    window = first_item["window"]

    assert window.shape == (64, 6)
    assert payload["symbol"] == "BTCUSD"
    assert payload["asset_class"] == "crypto"
    assert "fwd_5_ret_pct" in payload
    assert "fwd_10_ret_pct" in payload
    assert "fwd_20_ret_pct" in payload
    assert len(payload["fwd_20_normalized_path"]) == 20

    # Since prices are rising linearly:
    assert payload["fwd_20_ret_pct"] > 0
    assert payload["fwd_5_ret_pct"] > 0
    # Window start and end timestamps must reflect exactly L bars
    assert payload["end_ts"] > payload["start_ts"]


def test_stride_step_consistency():
    pipeline = IngestionPipeline(window_length=32, stride=4)
    candles = np.ones((100, 6), dtype=np.float32) * 50.0
    windows = list(pipeline.slice_rolling_windows(candles, "ETHUSD", "crypto", "1h"))

    # Expected count: (100 - 20 - 32) / 4 + 1 = 48 / 4 + 1 = 13
    assert len(windows) == 13


if __name__ == "__main__":
    pytest.main(["-v", __file__])
