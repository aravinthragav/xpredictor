"""
scripts/ingest_historical_indices.py
Fetches decades of real multi-asset historical data across major global indices,
commodities, and crypto:
- S&P 500 (^GSPC), NASDAQ 100 (^NDX), Dow Jones (^DJI)
- DAX 40 (^GDAXI), Nikkei 225 (^N225), FTSE 100 (^FTSE)
- Gold (GC=F, PAXGUSDT), Crude Oil (CL=F)
- Bitcoin (BTCUSDT), Ethereum (ETHUSDT)

Saves consolidated datasets to:
1. C:\\Users\\ragav\\OneDrive\\XPredictor_Data_Lake (auto-synced to cloud)
2. Local repository data_lake/
3. Generates a standalone ZIP archive for Google Drive upload.
"""

import os
import sys
import json
import time
import zipfile
import requests
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

ASSETS_YAHOO = [
    {"symbol": "SPX", "yahoo_ticker": "^GSPC", "name": "S&P 500 Index", "asset_class": "equities"},
    {"symbol": "NDX", "yahoo_ticker": "^NDX", "name": "NASDAQ 100 Index", "asset_class": "equities"},
    {"symbol": "DJI", "yahoo_ticker": "^DJI", "name": "Dow Jones Industrial Average", "asset_class": "equities"},
    {"symbol": "DAX", "yahoo_ticker": "^GDAXI", "name": "DAX 40 Index (Germany)", "asset_class": "equities"},
    {"symbol": "N225", "yahoo_ticker": "^N225", "name": "Nikkei 225 Index (Japan)", "asset_class": "equities"},
    {"symbol": "FTSE", "yahoo_ticker": "^FTSE", "name": "FTSE 100 Index (UK)", "asset_class": "equities"},
    {"symbol": "GOLD", "yahoo_ticker": "GC=F", "name": "Gold Futures / Spot", "asset_class": "fx_gold"},
    {"symbol": "OIL", "yahoo_ticker": "CL=F", "name": "WTI Crude Oil Futures", "asset_class": "commodities"},
]

ASSETS_BINANCE = [
    {"symbol": "BTCUSD", "binance_symbol": "BTCUSDT", "name": "Bitcoin / USD", "asset_class": "crypto"},
    {"symbol": "ETHUSD", "binance_symbol": "ETHUSDT", "name": "Ethereum / USD", "asset_class": "crypto"},
    {"symbol": "PAXGUSD", "binance_symbol": "PAXGUSDT", "name": "Paxos Gold Spot", "asset_class": "fx_gold"},
]


def fetch_yahoo_candles(ticker: str, period1: int = 0, period2: int = 2000000000, interval: str = "1d") -> List[Dict[str, Any]]:
    """Fetches full historical OHLCV from Yahoo Finance chart API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={period1}&period2={period2}&interval={interval}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            print(f"  [WARN] Yahoo API {ticker} returned {res.status_code}")
            return []
        
        result = res.json().get("chart", {}).get("result", [])
        if not result:
            return []
        
        data = result[0]
        timestamps = data.get("timestamp", [])
        indicators = data.get("indicators", {}).get("quote", [{}])[0]
        
        opens = indicators.get("open", [])
        highs = indicators.get("high", [])
        lows = indicators.get("low", [])
        closes = indicators.get("close", [])
        volumes = indicators.get("volume", [])
        
        candles = []
        for i, ts in enumerate(timestamps):
            o = opens[i] if i < len(opens) else None
            h = highs[i] if i < len(highs) else None
            l = lows[i] if i < len(lows) else None
            c = closes[i] if i < len(closes) else None
            v = volumes[i] if i < len(volumes) and volumes[i] is not None else 0
            
            if None not in (o, h, l, c):
                candles.append({
                    "timestamp": int(ts),
                    "open": round(float(o), 4),
                    "high": round(float(h), 4),
                    "low": round(float(l), 4),
                    "close": round(float(c), 4),
                    "volume": float(v)
                })
        return candles
    except Exception as e:
        print(f"  [ERROR] Failed to fetch {ticker}: {e}")
        return []


def fetch_binance_candles(symbol: str, interval: str = "1h", limit: int = 1000) -> List[Dict[str, Any]]:
    """Fetches high-resolution historical klines from Binance public API."""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            return []
        raw = res.json()
        candles = []
        for k in raw:
            candles.append({
                "timestamp": int(k[0] // 1000),
                "open": round(float(k[1]), 4),
                "high": round(float(k[2]), 4),
                "low": round(float(k[3]), 4),
                "close": round(float(k[4]), 4),
                "volume": round(float(k[5]), 4)
            })
        return candles
    except Exception as e:
        print(f"  [ERROR] Binance klines failed for {symbol}: {e}")
        return []


def main():
    print("=" * 70)
    print("XPredictor Institutional Multi-Asset Historical Data Lake Ingestion")
    print("=" * 70)

    # Output directories
    onedrive_dir = r"C:\Users\ragav\OneDrive\XPredictor_Data_Lake"
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_lake"))
    
    os.makedirs(onedrive_dir, exist_ok=True)
    os.makedirs(local_dir, exist_ok=True)

    summary = []
    total_candles = 0

    # 1. Fetch Major Global Indices & Commodities
    print("\n[Phase 1] Fetching Macro Daily & Intraday Indices from Global Exchanges...")
    for item in ASSETS_YAHOO:
        sym = item["symbol"]
        ticker = item["yahoo_ticker"]
        name = item["name"]
        asset_class = item["asset_class"]
        
        print(f"-> Fetching {name} ({sym}) [Daily Macro History]...")
        daily_candles = fetch_yahoo_candles(ticker, interval="1d")
        
        print(f"-> Fetching {name} ({sym}) [Intraday 1H Candles]...")
        # Yahoo gives 730 days of 1h
        now_ts = int(time.time())
        start_730d = now_ts - (720 * 86400)
        hourly_candles = fetch_yahoo_candles(ticker, period1=start_730d, period2=now_ts, interval="1h")

        count = len(daily_candles) + len(hourly_candles)
        total_candles += count

        dataset = {
            "symbol": sym,
            "name": name,
            "asset_class": asset_class,
            "yahoo_ticker": ticker,
            "daily_bars_count": len(daily_candles),
            "hourly_bars_count": len(hourly_candles),
            "date_range_daily": f"{time.strftime('%Y-%m-%d', time.gmtime(daily_candles[0]['timestamp']))} to {time.strftime('%Y-%m-%d', time.gmtime(daily_candles[-1]['timestamp']))}" if daily_candles else "N/A",
            "daily_candles": daily_candles,
            "hourly_candles": hourly_candles
        }

        # Save to JSON in both locations
        fname = f"{sym.lower()}_historical_dataset.json"
        for out_dir in [onedrive_dir, local_dir]:
            target_path = os.path.join(out_dir, fname)
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(dataset, f)

        summary.append({
            "symbol": sym,
            "name": name,
            "asset_class": asset_class,
            "daily_bars": len(daily_candles),
            "hourly_bars": len(hourly_candles),
            "total_bars": count
        })
        time.sleep(0.3)  # Respect rate limits

    # 2. Fetch Binance Crypto & Paxos Gold Spot
    print("\n[Phase 2] Fetching High-Resolution Crypto & Gold Spot from Binance...")
    for item in ASSETS_BINANCE:
        sym = item["symbol"]
        bsym = item["binance_symbol"]
        name = item["name"]
        asset_class = item["asset_class"]

        print(f"-> Fetching {name} ({sym}) [1H Klines]...")
        hourly_candles = fetch_binance_candles(bsym, interval="1h", limit=1000)
        
        print(f"-> Fetching {name} ({sym}) [15M Klines]...")
        m15_candles = fetch_binance_candles(bsym, interval="15m", limit=1000)

        count = len(hourly_candles) + len(m15_candles)
        total_candles += count

        dataset = {
            "symbol": sym,
            "name": name,
            "asset_class": asset_class,
            "binance_symbol": bsym,
            "hourly_bars_count": len(hourly_candles),
            "m15_bars_count": len(m15_candles),
            "hourly_candles": hourly_candles,
            "m15_candles": m15_candles
        }

        fname = f"{sym.lower()}_historical_dataset.json"
        for out_dir in [onedrive_dir, local_dir]:
            target_path = os.path.join(out_dir, fname)
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(dataset, f)

        summary.append({
            "symbol": sym,
            "name": name,
            "asset_class": asset_class,
            "daily_bars": 0,
            "hourly_bars": len(hourly_candles) + len(m15_candles),
            "total_bars": count
        })
        time.sleep(0.3)

    # 3. Create Consolidated Manifest and Google Drive Backup ZIP
    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        "total_assets": len(summary),
        "total_historical_bars": total_candles,
        "assets_summary": summary,
        "storage_paths": {
            "onedrive_sync_path": onedrive_dir,
            "local_repo_path": local_dir
        }
    }

    manifest_path_onedrive = os.path.join(onedrive_dir, "manifest.json")
    manifest_path_local = os.path.join(local_dir, "manifest.json")
    with open(manifest_path_onedrive, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    with open(manifest_path_local, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Package into a clean ZIP archive for Google Drive upload
    zip_dest = r"C:\Users\ragav\OneDrive\XPredictor_Historical_Indices_DataLake.zip"
    print(f"\n[Phase 3] Packaging into Google Drive upload ZIP: {zip_dest} ...")
    with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(onedrive_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, onedrive_dir)
                zf.write(file_path, arcname)

    zip_size_mb = os.path.getsize(zip_dest) / (1024 * 1024)

    print("\n" + "=" * 70)
    print("INGESTION COMPLETE:")
    print(f"Total Assets Processed:    {len(summary)}")
    print(f"Total Historical Candles:  {total_candles:,}")
    print(f"Cloud-Synced Folder:       {onedrive_dir}")
    print(f"Google Drive Backup ZIP:   {zip_dest} ({zip_size_mb:.2f} MB)")
    print("=" * 70)


if __name__ == "__main__":
    main()
