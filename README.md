# XPredictor

<div align="center">

![XPredictor Banner](https://img.shields.io/badge/XPredictor-2.0-8B5CF6?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Qdrant](https://img.shields.io/badge/Qdrant-v1.11+-red?style=for-the-badge&logo=qdrant)](https://qdrant.tech)

**Vectorized Price-Action Search Engine ("Shazam for Candlesticks") & Hybrid Reality Cone Terminal**

*Built on Foundation Market Model `shiyu-coder/Kronos` with Google Antigravity 2.0 Multi-Agent Orchestration*

</div>

---

## 📖 Overview

Traditional retail trading signal services fail due to severe macroeconomic blindness, discrete quantization noise, and negative customer retention economics. **XPredictor** productizes the mathematical strengths of the `Kronos` foundation model into a scalable, high-margin research terminal:

1. **Structural Microstructure Embeddings**: Uses `KronosTokenizer` (trained across 12B candles on 45 exchanges) to convert 6D candlestick sequences into scale-invariant 768-D structural vector representations.
2. **Sub-35ms Nearest Historical Analog Retrieval**: Indexes 50M+ multi-timeframe rolling windows across crypto, forex, equities, and commodities using Qdrant with HNSW and int8 scalar quantization.
3. **The Hybrid Reality Cone**: Fuses the empirical outcome distribution of the Top 100 historical analogs ($P_{\text{hist}}$) with 100 generative Monte Carlo forward paths ($P_{\text{gen}}$) sampled from Kronos, weighted by cosine similarity.
4. **Interactive Financial Canvas**: Next.js 15 + TradingView Lightweight Charts canvas enabling traders to brush 32 to 128 candles, view real-time statistical win rates, and replay historical twins as semi-transparent ghost overlays.

---

## 🤖 Antigravity 2.0 Multi-Agent Architecture

XPredictor is structured around four specialized autonomous agents defined under `.antigravity/agents/`:

```
                                  ┌─────────────────────────────┐
                                  │      Antigravity 2.0        │
                                  │       Manager Plane         │
                                  └──────────────┬──────────────┘
                                                 │
            ┌────────────────────┬───────────────┴───────────────┬────────────────────┐
            ▼                    ▼                               ▼                    ▼
   [Agent-01-QuantCore]  [Agent-02-VectorOps]           [Agent-03-TerminalUI]  [Agent-04-GrowthEngine]
   services/kronos-      services/ingestion-worker/     apps/web/              apps/web/src/growth/
   embedder/             & services/api/                                       & services/growth-bot/
   - Model wrapping      - Qdrant HNSW indexing         - Next.js 15 App       - Dynamic OG Cards
   - Causal norm         - Temporal anti-leakage        - TradingView canvas   - 1-Click Share to X
   - Monte Carlo cones   - Multi-asset ingestion        - Shift+Drag brush     - Embeddable Iframes
```

### Agent Roles & Guardrails

| Agent | Workspace | Verification Deliverable |
|---|---|---|
| **Agent-01-QuantCore** | `services/kronos-embedder/` | PyTest benchmark proving zero lookahead leakage & $<18\text{ms}$ embedding latency |
| **Agent-02-VectorOps** | `services/ingestion-worker/` & `services/api/` | Load-test proving $<35\text{ms}$ p95 ANN retrieval & temporal anti-leakage filters |
| **Agent-03-TerminalUI** | `apps/web/` | Interactive canvas with drag-selection rendering Reality Cone in $<150\text{ms}$ |
| **Agent-04-GrowthEngine** | `apps/web/src/growth/` & `services/growth-bot/` | 1200x630 OpenGraph cards, embeddable iframe widgets, macro catalyst bot |

### Global Agent Guardrails (`.antigravity/rules.md`)
1. **Strict Causal Normalization**: Rolling windows must be instance-normalized strictly using their own local window mean and standard deviation. No global or future statistics.
2. **Exclude Forward Leakage in Vector Retrieval**: Live pattern queries at timestamp $T_{\text{now}}$ must apply mandatory payload filters excluding historical windows overlapping $[T_{\text{now}} - L, T_{\text{now}}]$.
3. **Artifact-First PRs**: Every agent task must generate an Antigravity verification artifact (test suite log, latency benchmark, or visual preview).

---

## 📁 Repository Structure

```
xpredictor/
├── .antigravity/
│   ├── project.json                 # Monorepo workspace configuration
│   ├── rules.md                     # Quantitative and anti-leakage guardrails
│   └── agents/                      # Multi-agent definitions
│       ├── Agent-01-QuantCore.md
│       ├── Agent-02-VectorOps.md
│       ├── Agent-03-TerminalUI.md
│       └── Agent-04-GrowthEngine.md
├── apps/
│   └── web/                         # Next.js 15 Financial Canvas Terminal
│       ├── src/components/          # PatternTerminal, ChartCanvas, AnalogCarousel, ScoreCard
│       ├── src/growth/              # OpenGraph 1200x630 card generator
│       └── src/app/                 # App router, embed routes, and dynamic OG routes
├── services/
│   ├── kronos-embedder/             # Foundation model embedding microservice
│   │   ├── extractor.py             # KronosPatternEngine with attention pooling
│   │   ├── main.py                  # FastAPI /embed & /predict-cone endpoints
│   │   └── test_lookahead.py        # Verification tests for zero lookahead
│   ├── api/                         # Reality Cone orchestration API
│   │   ├── main.py                  # /api/v1/search-pattern endpoint
│   │   └── test_search_api.py       # API verification suite
│   ├── ingestion-worker/            # Async market data ingestion & Qdrant upsert
│   │   ├── pipeline.py              # Window slicer & forward outcome tracker
│   │   └── worker.py                # Universe ingestion cycle
│   └── growth-bot/                  # Automated macro catalyst social hijack bot
│       └── bot.py                   # High-engagement FinTwit publisher
├── infra/
│   └── docker/
│       ├── docker-compose.yml       # Qdrant, TimescaleDB, Redis, API, and workers
│       └── qdrant_init.py           # Int8 scalar quantization provisioning
├── XPREDICTOR_MASTER_PLAN.md        # Comprehensive engineering blueprint
└── README.md
```

---

## 🚀 Quick Start

### 1. Launch with Docker Compose
Clone the repository and spin up all services:

```bash
git clone https://github.com/aravinthragav/xpredictor.git
cd xpredictor

# Start Qdrant, TimescaleDB, Redis, Embedder, and API
docker compose -f infra/docker/docker-compose.yml up --build -d
```

### 2. Initialize Qdrant Partitioned Collections
Initialize the 3 window-partitioned vector collections (`w32`, `w64`, `w128`) with RAM-resident int8 scalar quantization:

```bash
python infra/docker/qdrant_init.py
```

### 3. Launch Web Terminal
```bash
cd apps/web
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to access the interactive pattern terminal.

---

## 🧪 Verification & Benchmark Tests

Run verification suites for QuantCore, VectorOps, and API services:

```bash
# Verify Zero Lookahead Leakage & Recency Weighting
pytest services/kronos-embedder/test_lookahead.py -v

# Verify Ingestion Rolling Window Mathematics
pytest services/ingestion-worker/test_ingestion.py -v

# Verify API Search and Reality Cone Endpoints
pytest services/api/test_search_api.py -v
```

---

## 📈 Go-To-Market & Growth Architecture

1. **Top-of-Funnel Conversion for aigoldforecast.com**: Convert existing gold traffic by providing 3 free historical analogs on daily gold charts with a high-converting CTA into XPredictor.
2. **Automated Macro Volatility Engine**: `services/growth-bot` triggers after CPI, FOMC, and NFP announcements, instantly generating branded 1200x630 OpenGraph cards with exact historical match dates and verifiable probabilities.
3. **Product-Led Growth (Embeddable Widgets)**: Financial newsletters (Substack, Beehiiv) embed interactive charts using:
   ```html
   <iframe src="https://xpredictor.com/embed/XAUUSD/1h?ref=affiliate_id" width="100%" height="600" frameborder="0"></iframe>
   ```
   Includes built-in 30% recurring creator affiliate commissions.
4. **B2B White-Label Licensing**: Embeddable pattern search widgets for retail brokers (Zerodha, Dhan, Bybit, Exness) priced at \$2,500–\$7,500/month.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
