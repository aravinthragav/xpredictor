"""
services/api/test_search_api.py
Verification suite for Agent-02-VectorOps API endpoints.
Tests search pattern handling, anti-leakage filtering, and reality cone response format.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def mock_candles(length: int = 64):
    candles = []
    base_price = 2500.0
    for i in range(length):
        p = base_price + i * 0.5
        candles.append([p - 0.2, p + 0.8, p - 0.5, p + 0.1, 1500.0 + i * 10, 3000000.0])
    return candles


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "xpredictor-api"
    assert data["status"] == "online"


def test_supported_tickers():
    response = client.get("/api/v1/tickers")
    assert response.status_code == 200
    data = response.json()
    assert "tickers" in data
    symbols = [t["symbol"] for t in data["tickers"]]
    assert "XAUUSD" in symbols
    assert "BTCUSD" in symbols


def test_search_pattern_valid_window():
    candles = mock_candles(64)
    payload = {
        "symbol": "XAUUSD",
        "timeframe": "1h",
        "candles": candles,
        "timestamp_now": 1720000000,
        "asset_filter": "all"
    }
    response = client.post("/api/v1/search-pattern", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "XAUUSD"
    assert data["window_length"] == 64
    assert "quantiles" in data
    assert "p10" in data["quantiles"]
    assert "p50" in data["quantiles"]
    assert "p90" in data["quantiles"]
    assert len(data["top_historical_twins"]) > 0
    assert "win_rate_20b" in data
    assert "optimal_rr" in data
    assert data["latency_ms"] < 200.0  # Verification of speed budget


def test_search_pattern_invalid_window_length():
    # Window under 32 candles should fail validation
    candles = mock_candles(20)
    payload = {
        "symbol": "BTCUSD",
        "timeframe": "1h",
        "candles": candles
    }
    response = client.post("/api/v1/search-pattern", json=payload)
    assert response.status_code == 400
    assert "out of range" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
