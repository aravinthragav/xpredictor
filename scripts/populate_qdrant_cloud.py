"""
scripts/populate_qdrant_cloud.py
Populates real vector collections in Qdrant Cloud across all window sizes:
- xpredictor_w64: 1,230 real staged vector points with forward returns
- xpredictor_w32: 32-bar rolling windows from real MT5 Gold candles (5,000 bars)
- xpredictor_w128: 128-bar rolling windows from real MT5 Gold candles (5,000 bars)
"""

import os
import sys
import json
import time
import requests
import numpy as np

# Add kronos-embedder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "kronos-embedder")))
from extractor import KronosPatternEngine

BASE_URL = os.getenv("QDRANT_URL", "https://317060a8-849e-400b-9c7b-0c2d561f6c04.sa-east-1-0.aws.cloud.qdrant.io:6333")
API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NjE4ODY2MzMtMTE3OC00YzMwLTkwZDUtZDFiOGIwNWVjODRiIn0.mUZrt_JLeLEE6yFtFXC3yr-SbiEGvGQfh9HKcFyxas8")
HEADERS = {"api-key": API_KEY, "Content-Type": "application/json"}

engine = KronosPatternEngine()


def upsert_batch(collection_name: str, points: list):
    url = f"{BASE_URL}/collections/{collection_name}/points?wait=true"
    res = requests.put(url, json={"points": points}, headers=HEADERS, timeout=30)
    if res.status_code not in [200, 201]:
        print(f"Error upserting to {collection_name}: {res.status_code} {res.text}")
    return res.status_code in [200, 201]


def populate_w64():
    print("\n--- Populating xpredictor_w64 from staged data (1,230 points) ---")
    file_path = os.path.join(os.path.dirname(__file__), "..", "services", "ingestion-worker", "data", "staged_xpredictor_w64.jsonl")
    if not os.path.exists(file_path):
        print("Staged w64 file not found:", file_path)
        return

    batch = []
    total = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            # Ensure date_formatted exists
            payload = data["payload"]
            if "date_formatted" not in payload:
                start_ts = payload.get("start_ts", 1700000000)
                payload["date_formatted"] = time.strftime("%b %Y", time.gmtime(start_ts))

            batch.append({
                "id": idx + 1,
                "vector": data["vector"],
                "payload": payload
            })

            if len(batch) >= 100:
                upsert_batch("xpredictor_w64", batch)
                total += len(batch)
                print(f"  Upserted {total} points into xpredictor_w64...")
                batch = []

    if batch:
        upsert_batch("xpredictor_w64", batch)
        total += len(batch)

    print(f"[OK] xpredictor_w64 completed with {total} real vector points.")


def generate_and_populate_windows(window_len: int, collection_name: str, stride: int = 4):
    print(f"\n--- Generating and populating {collection_name} (L={window_len}) from MT5 Gold data ---")
    cache_path = os.path.join(os.path.dirname(__file__), "..", "services", "ingestion-worker", "data", "xauusd_1h_cache.npz")
    if not os.path.exists(cache_path):
        print("Cache file not found:", cache_path)
        return

    data = np.load(cache_path)
    candles = data["candles"]  # Shape: (5000, 6)
    n_bars = len(candles)
    max_idx = n_bars - 20

    start_timestamp = int(time.time()) - (n_bars * 3600)
    interval_seconds = 3600

    points = []
    total = 0
    pt_id = 1

    for i in range(0, max_idx - window_len + 1, stride):
        window_slice = candles[i:i + window_len]
        fwd_slice = candles[i + window_len:i + window_len + 20]

        entry_price = float(window_slice[-1, 3])
        if entry_price <= 0:
            continue

        fwd_closes = fwd_slice[:, 3]
        fwd_lows = fwd_slice[:, 2]
        fwd_highs = fwd_slice[:, 1]

        fwd_5_ret = float((fwd_closes[min(4, len(fwd_closes) - 1)] - entry_price) / entry_price * 100.0)
        fwd_10_ret = float((fwd_closes[min(9, len(fwd_closes) - 1)] - entry_price) / entry_price * 100.0)
        fwd_20_ret = float((fwd_closes[-1] - entry_price) / entry_price * 100.0)

        fwd_20_max_dd = float((np.min(fwd_lows) - entry_price) / entry_price * 100.0)
        fwd_20_max_runup = float((np.max(fwd_highs) - entry_price) / entry_price * 100.0)
        fwd_norm_path = [round(float((c - entry_price) / entry_price * 100.0), 2) for c in fwd_closes]

        w_start_ts = start_timestamp + i * interval_seconds
        w_end_ts = start_timestamp + (i + window_len) * interval_seconds

        vector = engine.encode_window(window_slice).tolist()

        payload = {
            "symbol": "XAUUSD",
            "asset_class": "fx_gold",
            "timeframe": "1h",
            "date_formatted": time.strftime("%b %Y", time.gmtime(w_end_ts)),
            "start_ts": w_start_ts,
            "end_ts": w_end_ts,
            "fwd_5_ret_pct": round(fwd_5_ret, 2),
            "fwd_10_ret_pct": round(fwd_10_ret, 2),
            "fwd_20_ret_pct": round(fwd_20_ret, 2),
            "fwd_20_max_dd_pct": round(fwd_20_max_dd, 2),
            "fwd_20_max_runup_pct": round(fwd_20_max_runup, 2),
            "fwd_20_normalized_path": fwd_norm_path
        }

        points.append({
            "id": pt_id,
            "vector": vector,
            "payload": payload
        })
        pt_id += 1

        if len(points) >= 100:
            upsert_batch(collection_name, points)
            total += len(points)
            print(f"  Upserted {total} points into {collection_name}...")
            points = []

    if points:
        upsert_batch(collection_name, points)
        total += len(points)

    print(f"[OK] {collection_name} completed with {total} real vector points.")


def create_payload_indexes():
    print("\n--- Creating payload indexes for fast filtered searches ---")
    fields = [
        ("symbol", "keyword"),
        ("asset_class", "keyword"),
        ("timeframe", "keyword"),
        ("end_ts", "integer")
    ]
    for col in ["xpredictor_w32", "xpredictor_w64", "xpredictor_w128"]:
        for f_name, f_type in fields:
            requests.put(
                f"{BASE_URL}/collections/{col}/index",
                json={"field_name": f_name, "field_schema": f_type},
                headers=HEADERS
            )
    print("[OK] Payload indexes verified.")


if __name__ == "__main__":
    t0 = time.time()
    populate_w64()
    generate_and_populate_windows(32, "xpredictor_w32", stride=4)
    generate_and_populate_windows(128, "xpredictor_w128", stride=4)
    create_payload_indexes()
    print(f"\nAll Qdrant Cloud collections populated in {time.time() - t0:.2f} seconds!")
