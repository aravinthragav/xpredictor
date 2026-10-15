# Agent-02-VectorOps

**Workspace**: `services/ingestion-worker/` & `services/api/`
**Role**: Vector Infrastructure & High-Throughput Search Architect

## Primary Responsibilities
1. Configure and manage vector infrastructure:
   - **Qdrant (v1.11+)** partitioned into 3 collections: `xpredictor_w32`, `xpredictor_w64`, `xpredictor_w128`.
   - Index parameters: HNSW `m=32`, `ef_construct=200`, `distance=Cosine`, `on_disk=true`.
   - Int8 scalar quantization (`quantile=0.99`, `always_ram=true`) compressing index footprint by 75% to ~38 GB RAM for 50M+ vectors.
   - **TimescaleDB (pg16)** for raw historical 15m, 1H, 4H, and 1D OHLCV storage across 5,000+ global assets.
2. Ingestion pipeline:
   - Async ingestion of historical candles (Binance crypto, Polygon/Databento equities, FX XAU/USD, EUR/USD, indices NAS100, S&P 500).
   - Slicing rolling windows of $L \in \{32, 64, 128\}$ with stride $S=4$.
   - Pre-computing forward 5, 10, and 20-bar percentage returns, max drawdowns, and normalized path vectors directly in Qdrant JSON payload.
3. Fast similarity and reality cone API:
   - `POST /api/v1/search-pattern`: Encodes queried candle brush, performs cosine similarity search ($d_{\text{cosine}} \ge 0.82$), filters out contemporaneous self-matches ($[T_{\text{now}} - L, T_{\text{now}}]$), fetches Top-100 historical analogs, requests 100 generative forward paths from `kronos-embedder`, and computes the Bayesian Ensemble Reality Cone.

## Verification Artifact Required
Load-test report / pytest benchmark proving $<35\text{ms}$ p95 Top-100 ANN retrieval across vectors and verified temporal anti-leakage filters.
