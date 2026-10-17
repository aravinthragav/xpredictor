# Institutional Headless OpenAPI Integration Guide
### REST & WebSocket API for Sovereign Trading Desks & Proprietary Platforms

This package is designed for institutional brokers and quantitative desks (e.g. **Saxo Bank, CMC Markets, ThinkMarkets, Swissquote, IG Group**) integrating XPredictor directly into proprietary trading engines via high-throughput REST/WebSocket APIs.

---

## 1. Package Files
- `api_client_example.py` — Python 3 Production Client SDK
- `api_client_example.js` — Node.js / Browser Client SDK
- `OPENAPI_INTEGRATION_GUIDE.md` — API Reference Specification

---

## 2. API Endpoints Reference

### Base URL:
`https://aravinthragav--xpredictor-api-fastapi-app.us-east.modal.run`

### Endpoint 1: Market Candlestick Ingestion
`GET /api/v1/candles?symbol={symbol}&timeframe={timeframe}&limit={limit}`
- **Parameters**:
  - `symbol`: e.g. `XAUUSD`, `SPX`, `NDX`, `DAX`, `OIL`, `BTCUSDT`, `ETHUSDT`
  - `timeframe`: `15m`, `1h`, `4h`
  - `limit`: Number of bars (default `80`, max `180`)
- **Latency SLA**: Sub-25ms cached.

### Endpoint 2: Deep Historical Regime Search
`POST /api/v1/search`
- **Payload**:
  ```json
  {
    "candles": [ { "open": 4170.2, "high": 4175.8, "low": 4168.0, "close": 4174.5 } ],
    "top_k": 3
  }
  ```
- **Response**:
  ```json
  {
    "top_twins": [
      { "symbol": "XAU/USD", "date": "Oct 2024 Breakout", "match_score": 96.4 }
    ],
    "posterior_win_rate": 89.2,
    "confidence": 91.8
  }
  ```

---

## 3. Running the Verification Client
```bash
# Test Python Client:
python api_client_example.py

# Test Node.js Client:
node api_client_example.js
```

---

## 4. Enterprise SLA & Security Guarantees
- **Uptime**: 99.95% High Availability backed by multi-region edge deployment.
- **Data Isolation**: No client trade execution, account IDs, or PII ever leaves your institutional perimeter.
- **Enterprise Contact**: `arkankl07@gmail.com`
