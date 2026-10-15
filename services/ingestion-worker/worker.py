"""
services/ingestion-worker/worker.py
Continuous background worker ingesting crypto, FX, equities, and commodities.
"""

import time
import logging
import numpy as np
from pipeline import IngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TARGET_ASSETS = [
    {"symbol": "XAUUSD", "asset_class": "commodities", "timeframe": "1h"},
    {"symbol": "BTCUSD", "asset_class": "crypto", "timeframe": "1h"},
    {"symbol": "ETHUSD", "asset_class": "crypto", "timeframe": "1h"},
    {"symbol": "EURUSD", "asset_class": "fx_gold", "timeframe": "1h"},
    {"symbol": "NAS100", "asset_class": "equities", "timeframe": "1h"},
    {"symbol": "NVDA", "asset_class": "equities", "timeframe": "1h"},
    {"symbol": "SPY", "asset_class": "equities", "timeframe": "1h"},
]


def generate_sample_dataset(bars: int = 1500) -> np.ndarray:
    """Generates continuous historical candle series for indexing."""
    np.random.seed(42)
    p = 2000.0
    candles = []
    for _ in range(bars):
        ret = np.random.normal(0.0001, 0.007)
        p = max(10.0, p * (1.0 + ret))
        high = p * (1.0 + abs(np.random.normal(0, 0.003)))
        low = p * (1.0 - abs(np.random.normal(0, 0.003)))
        open_p = low + np.random.uniform(0.2, 0.8) * (high - low)
        close_p = low + np.random.uniform(0.2, 0.8) * (high - low)
        vol = float(np.random.lognormal(mean=8.5, sigma=0.6))
        amt = vol * close_p
        candles.append([open_p, high, low, close_p, vol, amt])
    return np.array(candles, dtype=np.float32)


def run_ingestion_cycle():
    pipeline_64 = IngestionPipeline(window_length=64, stride=4)
    total_upserted = 0

    logging.info("Starting XPredictor ingestion cycle across universe...")
    for asset in TARGET_ASSETS:
        candles = generate_sample_dataset(1200)
        batch = []
        for item in pipeline_64.slice_rolling_windows(
            candles,
            symbol=asset["symbol"],
            asset_class=asset["asset_class"],
            timeframe=asset["timeframe"]
        ):
            batch.append(item)
            if len(batch) >= 64:
                count = pipeline_64.batch_encode_and_upsert(batch)
                total_upserted += count
                batch = []

        if batch:
            count = pipeline_64.batch_encode_and_upsert(batch)
            total_upserted += count

        logging.info(f"Indexed {asset['symbol']} ({asset['timeframe']}) windows.")

    logging.info(f"Ingestion cycle completed. Total windows upserted: {total_upserted}")


if __name__ == "__main__":
    while True:
        try:
            run_ingestion_cycle()
        except Exception as e:
            logging.error(f"Worker cycle failed: {e}")
        time.sleep(3600)  # Ingest once per hour
