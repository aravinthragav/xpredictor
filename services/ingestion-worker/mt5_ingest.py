"""
services/ingestion-worker/mt5_ingest.py
Pulls historical K-line chart data directly from MetaTrader 5 (MT5),
slices causal rolling windows, extracts forward returns/drawdowns,
and indexes vectors into Qdrant (or caches locally).
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime
import numpy as np

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False

from pipeline import IngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TIMEFRAME_MAP = {
    "15m": mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 15,
    "1h": mt5.TIMEFRAME_H1 if MT5_AVAILABLE else 60,
    "4h": mt5.TIMEFRAME_H4 if MT5_AVAILABLE else 240,
    "1d": mt5.TIMEFRAME_D1 if MT5_AVAILABLE else 1440,
}


def connect_mt5(path: str = None) -> bool:
    """Connects to local MetaTrader 5 terminal."""
    if not MT5_AVAILABLE:
        logging.error("MetaTrader5 package is not available.")
        return False

    default_paths = [
        path,
        r"C:\Program Files\MetaTrader 5\terminal64.exe",
        r"C:\Program Files\MetaTrader 5 IC Markets (SC)\terminal64.exe"
    ]
    terminal_path = next((p for p in default_paths if p and os.path.exists(p)), None)

    if terminal_path:
        logging.info(f"Connecting to MT5 terminal at: {terminal_path}")
        connected = mt5.initialize(path=terminal_path)
    else:
        logging.info("Attempting default MT5 initialize...")
        connected = mt5.initialize()

    if not connected:
        logging.error(f"MT5 initialization failed, error code: {mt5.last_error()}")
        return False

    terminal_info = mt5.terminal_info()
    if terminal_info:
        logging.info(f"Connected to MT5: {terminal_info.name} (Build {terminal_info.build})")
    return True


def fetch_mt5_candles(symbol: str = "XAUUSD", timeframe_str: str = "1h", num_bars: int = 50000) -> np.ndarray:
    """Fetches historical OHLCV data from MT5 for the specified symbol and timeframe."""
    if not MT5_AVAILABLE:
        raise RuntimeError("MetaTrader5 package not available")

    # Ensure symbol is visible in Market Watch
    if not mt5.symbol_select(symbol, True):
        # Try finding case variants e.g. GOLD, XAUUSDm, XAUUSD.a
        all_symbols = [s.name for s in mt5.symbols_get() or []]
        match = next((s for s in all_symbols if symbol.lower() in s.lower() or "gold" in s.lower()), None)
        if match:
            logging.info(f"Remapping requested '{symbol}' to detected broker symbol: '{match}'")
            symbol = match
            mt5.symbol_select(symbol, True)
        else:
            raise RuntimeError(f"Symbol '{symbol}' not found in MT5 symbols")

    tf = TIMEFRAME_MAP.get(timeframe_str.lower(), mt5.TIMEFRAME_H1)
    logging.info(f"Requesting {num_bars} bars for {symbol} on {timeframe_str.upper()}...")

    rates = mt5.copy_rates_from_pos(symbol, tf, 0, num_bars)
    if rates is None or len(rates) == 0:
        raise RuntimeError(f"No rates returned for {symbol} ({mt5.last_error()})")

    logging.info(f"Retrieved {len(rates)} bars from MT5 for {symbol}.")

    # Format into (N, 6): [open, high, low, close, volume, amount]
    candles = []
    for r in rates:
        open_p = float(r["open"])
        high_p = float(r["high"])
        low_p = float(r["low"])
        close_p = float(r["close"])
        vol = float(r["tick_volume"] if r["tick_volume"] > 0 else 1.0)
        amt = vol * close_p
        candles.append([open_p, high_p, low_p, close_p, vol, amt])

    return np.array(candles, dtype=np.float32)


def ingest_mt5_data(
    symbol: str = "XAUUSD",
    timeframe: str = "1h",
    bars: int = 20000,
    window_length: int = 64,
    stride: int = 4,
    save_cache: bool = True
):
    """Full pipeline: MT5 fetch -> causal window slice -> outcome calculation -> vector indexing."""
    if not connect_mt5():
        logging.warning("MT5 terminal unavailable. Generating synthetic gold series for validation.")
        # Fallback synthetic gold series for immediate testing
        from worker import generate_sample_dataset
        candles = generate_sample_dataset(bars=min(bars, 2000))
    else:
        try:
            candles = fetch_mt5_candles(symbol, timeframe, bars)
        finally:
            mt5.shutdown()

    logging.info(f"Processing {len(candles)} candles for {symbol}...")
    pipeline = IngestionPipeline(window_length=window_length, stride=stride)

    batch = []
    total_indexed = 0
    t0 = time.time()

    for item in pipeline.slice_rolling_windows(
        candles,
        symbol=symbol,
        asset_class="commodities" if "xau" in symbol.lower() or "gold" in symbol.lower() else "forex",
        timeframe=timeframe
    ):
        batch.append(item)
        if len(batch) >= 64:
            count = pipeline.batch_encode_and_upsert(batch)
            total_indexed += count
            batch = []

    if batch:
        count = pipeline.batch_encode_and_upsert(batch)
        total_indexed += count

    elapsed = round(time.time() - t0, 2)
    logging.info(f"Ingestion completed: {total_indexed} rolling windows indexed in {elapsed}s.")

    # Save local cache artifact
    if save_cache:
        os.makedirs("data", exist_ok=True)
        cache_path = os.path.join("data", f"{symbol.lower()}_{timeframe}_cache.npz")
        np.savez_compressed(cache_path, candles=candles)
        logging.info(f"Historical candles saved to cache: {cache_path}")

    return total_indexed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MT5 Historical Data Ingestion for XPredictor")
    parser.add_argument("--symbol", type=str, default="XAUUSD", help="Symbol to pull from MT5")
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe (15m, 1h, 4h, 1d)")
    parser.add_argument("--bars", type=int, default=10000, help="Number of bars to pull")
    parser.add_argument("--window", type=int, default=64, help="Rolling window size L")
    parser.add_argument("--stride", type=int, default=4, help="Stride step S")

    args = parser.parse_args()
    ingest_mt5_data(
        symbol=args.symbol,
        timeframe=args.timeframe,
        bars=args.bars,
        window_length=args.window,
        stride=args.stride
    )
