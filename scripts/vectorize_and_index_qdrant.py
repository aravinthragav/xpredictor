"""
scripts/vectorize_and_index_qdrant.py
Generates 768-D scale-invariant Kronos embeddings across multi-asset historical datasets:
- U.S. Indices: S&P 500 (SPX), NASDAQ 100 (NDX), Dow Jones (DJI)
- Global Indices: DAX 40 (DAX), Nikkei 225 (N225), FTSE 100 (FTSE)
- Commodities & FX: Gold (GOLD/XAUUSD), Crude Oil (OIL)
- Crypto: Bitcoin (BTCUSD), Ethereum (ETHUSD), Paxos Gold (PAXGUSD)

Tags each window with:
- Market Session: Asian, London, London/NY Overlap, New York, Pacific
- Volatility Regime: Low Vol (Compression), Normal Volatility, High Vol (Expansion), Extreme Vol (Shock)
- Macro Event & Trend Regime: COVID Shock, Fed Hike Cycle, SVB Banking Stress, AI Boom, Gold Supercycle
- Scale-Invariant Causal Embeddings + Forward 20-bar trajectory

Populates Qdrant Cloud collections:
- xpredictor_w32 (32-bar windows)
- xpredictor_w64 (64-bar windows)
- xpredictor_w128 (128-bar windows)
All enabled with int8 Scalar Quantization for sub-20ms speed and <10% Free Tier RAM usage.
"""

import os
import sys
import json
import time
import requests
import numpy as np
from typing import List, Dict, Any, Tuple

# Add kronos-embedder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "kronos-embedder")))
from extractor import KronosPatternEngine

BASE_URL = os.getenv("QDRANT_URL", "https://317060a8-849e-400b-9c7b-0c2d561f6c04.sa-east-1-0.aws.cloud.qdrant.io:6333")
API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NjE4ODY2MzMtMTE3OC00YzMwLTkwZDUtZDFiOGIwNWVjODRiIn0.mUZrt_JLeLEE6yFtFXC3yr-SbiEGvGQfh9HKcFyxas8")
HEADERS = {"api-key": API_KEY, "Content-Type": "application/json"}

engine = KronosPatternEngine()

DATA_DIRS = [
    r"C:\Users\ragav\OneDrive\XPredictor_Data_Lake",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_lake"))
]


def init_collection(name: str):
    """Recreates collection with int8 Scalar Quantization and disk payload."""
    print(f"\n[Qdrant] Initializing collection: {name} (768-D, Cosine, int8 Quantized)...")
    requests.delete(f"{BASE_URL}/collections/{name}", headers=HEADERS)
    time.sleep(1)

    payload = {
        "vectors": {
            "size": 768,
            "distance": "Cosine"
        },
        "quantization_config": {
            "scalar": {
                "type": "int8",
                "quantile": 0.99,
                "always_ram": True
            }
        },
        "on_disk_payload": True,
        "hnsw_config": {
            "m": 16,
            "ef_construct": 100,
            "on_disk": False
        }
    }
    r = requests.put(f"{BASE_URL}/collections/{name}", json=payload, headers=HEADERS)
    if r.status_code in [200, 201]:
        print(f"  Collection {name} created successfully.")
    else:
        print(f"  Error creating {name}: {r.status_code} {r.text}")

    # Create payload indexes
    indexes = [
        ("symbol", "keyword"),
        ("asset_class", "keyword"),
        ("timeframe", "keyword"),
        ("session", "keyword"),
        ("vol_regime", "keyword"),
        ("macro_regime", "keyword"),
        ("end_ts", "integer")
    ]
    for field_name, field_type in indexes:
        requests.put(
            f"{BASE_URL}/collections/{name}/index",
            json={"field_name": field_name, "field_schema": field_type},
            headers=HEADERS
        )


def get_session_name(ts: int) -> str:
    utc_hour = time.gmtime(ts).tm_hour
    if 0 <= utc_hour < 7:
        return "Asian (Tokyo/Sydney)"
    elif 7 <= utc_hour < 12:
        return "London (Europe Open)"
    elif 12 <= utc_hour < 16:
        return "London/NY Overlap (Peak Liquidity)"
    elif 16 <= utc_hour < 21:
        return "New York (US Afternoon)"
    else:
        return "Pacific / Late Session"


def get_vol_regime(window: np.ndarray) -> str:
    returns = np.diff(window[:, 3]) / (window[:-1, 3] + 1e-8)
    vol_pct = float(np.std(returns) * np.sqrt(len(returns)) * 100.0) if len(returns) > 1 else 1.5
    if vol_pct < 1.0:
        return "Low Vol (Compression)"
    elif vol_pct < 2.5:
        return "Normal Volatility"
    elif vol_pct < 5.0:
        return "High Vol (Expansion)"
    else:
        return "Extreme Vol (Market Shock)"


def get_macro_regime(window: np.ndarray, end_ts: int) -> str:
    tm = time.gmtime(end_ts)
    year, month = tm.tm_year, tm.tm_mon

    if year == 2020 and month in [2, 3, 4]:
        return "COVID-19 Liquidity Shock"
    elif year == 2022 and month in [1, 3, 5, 6, 9]:
        return "Aggressive Fed Rate Hike Cycle"
    elif year == 2023 and month in [3, 4]:
        return "US Regional Banking Stress (SVB)"
    elif year == 2024 and month in [1, 2, 3, 4, 5]:
        return "AI / Semiconductor Expansion"
    elif year == 2024 and month in [10, 11]:
        return "US Election Regime Shift"
    elif year >= 2025:
        return "Commodity & Gold Supercycle"

    ret = (window[-1, 3] - window[0, 3]) / (window[0, 3] + 1e-8) * 100.0
    if ret > 2.5:
        return "Bullish Trend Breakout"
    elif ret < -2.5:
        return "Bearish Liquidity Flush"
    elif abs(ret) < 0.8:
        return "Mean-Reversion Consolidation"
    else:
        return "Directional Trend Expansion"


def load_all_datasets() -> List[Dict[str, Any]]:
    """Loads all asset files from data lake directory."""
    target_dir = None
    for d in DATA_DIRS:
        if os.path.exists(d) and os.path.exists(os.path.join(d, "manifest.json")):
            target_dir = d
            break
    if not target_dir:
        raise RuntimeError("Data lake directory not found in candidates!")

    print(f"[DataLoader] Reading datasets from: {target_dir}")
    datasets = []
    for fname in os.listdir(target_dir):
        if fname.endswith("_historical_dataset.json"):
            fpath = os.path.join(target_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                datasets.append(json.load(f))
    print(f"[DataLoader] Successfully loaded {len(datasets)} asset datasets.")
    return datasets


def candles_to_matrix(candle_list: List[Dict[str, Any]]) -> np.ndarray:
    """Converts candle dicts into (N, 6) numpy array [O, H, L, C, V, Amount] + timestamps."""
    if not candle_list:
        return np.empty((0, 7), dtype=np.float64)
    rows = []
    for c in candle_list:
        op = float(c["open"])
        hi = float(c["high"])
        lo = float(c["low"])
        cl = float(c["close"])
        vol = float(c.get("volume", 0.0))
        amt = vol * cl
        ts = float(c.get("timestamp", 0))
        rows.append([op, hi, lo, cl, vol, amt, ts])
    return np.array(rows, dtype=np.float64)


def upsert_batch(collection_name: str, points: list):
    url = f"{BASE_URL}/collections/{collection_name}/points?wait=true"
    res = requests.put(url, json={"points": points}, headers=HEADERS, timeout=40)
    if res.status_code not in [200, 201]:
        print(f"    [WARN] Upsert failed ({res.status_code}): {res.text[:200]}")
    return res.status_code in [200, 201]


def process_collection(collection_name: str, window_len: int, datasets: List[Dict[str, Any]]):
    print(f"\n{'='*70}")
    print(f"PROCESSING COLLECTION: {collection_name} (Window Length = {window_len} bars)")
    print(f"{'='*70}")

    init_collection(collection_name)

    points_batch = []
    total_upserted = 0
    pt_id = 1

    for ds in datasets:
        sym = ds["symbol"]
        asset_class = ds.get("asset_class", "equities")
        name = ds.get("name", sym)

        series_to_process = []
        # Intraday series (1H)
        if ds.get("hourly_candles"):
            series_to_process.append(("1h", candles_to_matrix(ds["hourly_candles"]), 4))  # stride 4
        # Daily macro series
        if ds.get("daily_candles"):
            series_to_process.append(("1d", candles_to_matrix(ds["daily_candles"]), 8))   # stride 8
        # 15M crypto series
        if ds.get("m15_candles"):
            series_to_process.append(("15m", candles_to_matrix(ds["m15_candles"]), 6))   # stride 6

        asset_points = 0
        for tf, mat, stride in series_to_process:
            if len(mat) < window_len + 20:
                continue

            max_idx = len(mat) - 20
            for i in range(0, max_idx - window_len + 1, stride):
                w_mat = mat[i:i + window_len, :6]
                fwd_mat = mat[i + window_len:i + window_len + 20, :6]
                end_ts = int(mat[i + window_len - 1, 6])
                start_ts = int(mat[i, 6])

                entry_price = float(w_mat[-1, 3])
                if entry_price <= 0:
                    continue

                fwd_closes = fwd_mat[:, 3]
                fwd_lows = fwd_mat[:, 2]
                fwd_highs = fwd_mat[:, 1]

                fwd_5_ret = float((fwd_closes[min(4, len(fwd_closes) - 1)] - entry_price) / entry_price * 100.0)
                fwd_10_ret = float((fwd_closes[min(9, len(fwd_closes) - 1)] - entry_price) / entry_price * 100.0)
                fwd_20_ret = float((fwd_closes[-1] - entry_price) / entry_price * 100.0)

                fwd_20_max_dd = float((np.min(fwd_lows) - entry_price) / entry_price * 100.0)
                fwd_20_max_runup = float((np.max(fwd_highs) - entry_price) / entry_price * 100.0)
                fwd_norm_path = [round(float((c - entry_price) / entry_price * 100.0), 2) for c in fwd_closes]

                # Generate 768-D structural embedding
                vector = engine.encode_window(w_mat).tolist()

                # Microstructure and macro regime tags
                session_tag = get_session_name(end_ts)
                vol_tag = get_vol_regime(w_mat)
                macro_tag = get_macro_regime(w_mat, end_ts)
                date_fmt = time.strftime("%b %Y", time.gmtime(end_ts))

                payload = {
                    "symbol": sym,
                    "name": name,
                    "asset_class": asset_class,
                    "timeframe": tf,
                    "session": session_tag,
                    "vol_regime": vol_tag,
                    "macro_regime": macro_tag,
                    "date_formatted": date_fmt,
                    "start_ts": start_ts,
                    "end_ts": end_ts,
                    "fwd_5_ret_pct": round(fwd_5_ret, 2),
                    "fwd_10_ret_pct": round(fwd_10_ret, 2),
                    "fwd_20_ret_pct": round(fwd_20_ret, 2),
                    "fwd_20_max_dd_pct": round(fwd_20_max_dd, 2),
                    "fwd_20_max_runup_pct": round(fwd_20_max_runup, 2),
                    "fwd_20_normalized_path": fwd_norm_path
                }

                points_batch.append({
                    "id": pt_id,
                    "vector": vector,
                    "payload": payload
                })
                pt_id += 1
                asset_points += 1

                if len(points_batch) >= 200:
                    upsert_batch(collection_name, points_batch)
                    total_upserted += len(points_batch)
                    points_batch = []

        print(f"  -> {sym:7s} ({name[:25]:25s}): Indexed {asset_points:5d} pattern vectors.")

    if points_batch:
        upsert_batch(collection_name, points_batch)
        total_upserted += len(points_batch)

    print(f"\n[OK] Collection {collection_name} indexing complete: {total_upserted:,} vectors indexed.")
    return total_upserted


def main():
    t_start = time.time()
    print("=" * 70)
    print("XPredictor Multi-Asset High-Density Vector Ingestion Engine")
    print(f"Target Cluster: {BASE_URL}")
    print("Compression:    int8 Scalar Quantization (4x memory reduction)")
    print("=" * 70)

    datasets = load_all_datasets()

    counts = {}
    counts["w32"] = process_collection("xpredictor_w32", 32, datasets)
    counts["w64"] = process_collection("xpredictor_w64", 64, datasets)
    counts["w128"] = process_collection("xpredictor_w128", 128, datasets)

    total_all = sum(counts.values())
    total_time = time.time() - t_start

    print("\n" + "=" * 70)
    print("VECTORIZATION & INDEXING COMPLETE:")
    print(f"xpredictor_w32:   {counts['w32']:,} points")
    print(f"xpredictor_w64:   {counts['w64']:,} points")
    print(f"xpredictor_w128:  {counts['w128']:,} points")
    print(f"Total Vectors:    {total_all:,} 768-D multi-asset vectors")
    print(f"Elapsed Time:     {total_time:.1f} seconds")
    print("=" * 70)


if __name__ == "__main__":
    main()
