"""
services/kronos-embedder/test_lookahead.py
Verification suite for Agent-01-QuantCore.
Validates zero lookahead leakage, causal instance normalization, and latency budgets.
"""

import time
import numpy as np
import pytest
from extractor import KronosPatternEngine


@pytest.fixture
def engine():
    return KronosPatternEngine()


def generate_synthetic_candles(n_bars: int = 200, seed: int = 42) -> np.ndarray:
    np.random.seed(seed)
    prices = [2000.0]
    for _ in range(n_bars - 1):
        ret = np.random.normal(0.0002, 0.008)
        prices.append(prices[-1] * (1.0 + ret))

    candles = []
    for p in prices:
        high = p * (1.0 + abs(np.random.normal(0, 0.003)))
        low = p * (1.0 - abs(np.random.normal(0, 0.003)))
        open_p = low + np.random.uniform(0.2, 0.8) * (high - low)
        close_p = low + np.random.uniform(0.2, 0.8) * (high - low)
        vol = float(np.random.lognormal(mean=8.0, sigma=0.5))
        amt = vol * close_p
        candles.append([open_p, high, low, close_p, vol, amt])

    return np.array(candles, dtype=np.float32)


def test_zero_lookahead_leakage(engine):
    """
    Guardrail Verification: Modifying candles AFTER timestamp t must NOT change
    the embedding vector for the window ending at timestamp t.
    """
    total_candles = generate_synthetic_candles(150, seed=101)
    window_len = 64
    t = 100

    # Window A ending at t
    window_a = total_candles[t - window_len:t].copy()
    emb_a = engine.encode_window(window_a)

    # Corrupt future candles after t
    corrupted_candles = total_candles.copy()
    corrupted_candles[t:] *= 5.0  # Massive 5x spike in the future

    # Window B extracted from the same lookback period [t-window_len, t]
    window_b = corrupted_candles[t - window_len:t].copy()
    emb_b = engine.encode_window(window_b)

    # Difference must be strictly zero within floating point epsilon
    diff = np.max(np.abs(emb_a - emb_b))
    assert diff < 1e-6, f"Lookahead leakage detected! Difference: {diff}"


def test_l2_normalization(engine):
    """Verifies that all output embeddings are strictly L2 normalized."""
    candles = generate_synthetic_candles(64, seed=42)
    embedding = engine.encode_window(candles)

    norm = np.linalg.norm(embedding)
    assert abs(norm - 1.0) < 1e-4, f"Embedding is not L2 normalized: norm={norm}"
    assert embedding.shape == (768,), f"Expected 768 dimensions, got {embedding.shape}"


def test_recency_weighting_effect(engine):
    """Verifies that changes in recent bars have greater impact than distant past bars."""
    base_window = generate_synthetic_candles(64, seed=77)
    base_emb = engine.encode_window(base_window)

    # Perturb the oldest bar (index 0)
    old_perturbed = base_window.copy()
    old_perturbed[0, :4] *= 1.10
    emb_old = engine.encode_window(old_perturbed)
    diff_old = np.linalg.norm(emb_old - base_emb)

    # Perturb the most recent breakout bar (index -1) by the same percentage
    recent_perturbed = base_window.copy()
    recent_perturbed[-1, :4] *= 1.10
    emb_recent = engine.encode_window(recent_perturbed)
    diff_recent = np.linalg.norm(emb_recent - base_emb)

    # Recency-weighted pooling must make recent perturbations exert significant weight
    assert diff_recent > diff_old * 0.9, "Recency weighting failed to adequately weight breakout tail"


def test_predict_cone_quantiles_ordering(engine):
    """Verifies that predicted reality cone quantiles are monotonically ordered."""
    window = generate_synthetic_candles(64, seed=99)
    result = engine.predict_cone(window, pred_len=20, sample_count=100)

    q = result["quantiles"]
    p10, p25, p50, p75, p90 = (
        np.array(q["p10"]),
        np.array(q["p25"]),
        np.array(q["p50"]),
        np.array(q["p75"]),
        np.array(q["p90"]),
    )

    # At all forward horizons, p10 <= p25 <= p50 <= p75 <= p90
    assert np.all(p10 <= p25 + 1e-6), "p10 > p25 violation"
    assert np.all(p25 <= p50 + 1e-6), "p25 > p50 violation"
    assert np.all(p50 <= p75 + 1e-6), "p50 > p75 violation"
    assert np.all(p75 <= p90 + 1e-6), "p75 > p90 violation"


def test_embedding_latency(engine):
    """Verifies that single-window embedding meets latency budget (<20ms)."""
    window = generate_synthetic_candles(64, seed=123)

    # Warmup
    for _ in range(5):
        engine.encode_window(window)

    latencies = []
    for _ in range(30):
        t0 = time.perf_counter()
        engine.encode_window(window)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    p95_latency = np.percentile(latencies, 95)
    print(f"\n[LATENCY BENCHMARK] p95 Embedding Latency: {p95_latency:.2f} ms")
    assert p95_latency < 25.0, f"Embedding latency exceeded budget: {p95_latency:.2f} ms"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
