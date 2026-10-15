# XPredictor: Vectorized Price-Action Search Engine ("Shazam for Candlesticks") & Hybrid Reality Cone Terminal

> **Master Architecture Specification & Engineering Blueprint**  
> *Antigravity 2.0 Multi-Agent Monorepo Implementation*

---

## 1. Executive Summary & Product Vision

Retail trading products that sell single-asset point predictions (e.g. directional calls like "BUY Gold at \$2,650") suffer from catastrophic structural churn (30%–55% monthly) and adverse unit economics. Financial price series are non-stationary, macro-dominated, and exhibit heavy tails where point forecasts quickly decay to a martingale after spread and slippage.

**XPredictor** transforms the paradigm by adapting foundation market models (`shiyu-coder/Kronos`) into an institutional-grade **Vectorized Price-Action Search Engine and Hybrid Reality Cone Terminal**:
1. **Financial Microstructure Tokenization**: Uses the hierarchical discrete codebooks of `KronosTokenizer` (trained on 12 billion candles across 45 global exchanges) to generate scale-invariant 768-D structural embeddings of price-volume action.
2. **Sub-35ms Nearest Historical Analog Retrieval**: Indexes 50M+ multi-timeframe rolling windows across crypto, FX, equities, and commodities in a low-latency Qdrant HNSW vector database with int8 scalar quantization.
3. **Hybrid Reality Cone Algorithm**: Fuses the empirical forward trajectory distribution of the Top 100 historical analogs ($P_{\text{hist}}$) with 100 generative forward paths ($P_{\text{gen}}$) sampled via Monte Carlo token simulation from Kronos-base, weighted by cosine similarity.
4. **Interactive Financial Canvas**: Next.js 15 + TradingView Lightweight Charts canvas enabling traders to brush any 32- to 128-bar chart setup and receive an instant statistical reality cone, win-rate breakdown, and ghost analog overlay in $<150\text{ms}$.

---

## 2. Multi-Agent Orchestration Architecture

To develop and maintain this system without architectural debt, Google Antigravity 2.0 orchestrates four autonomous agents operating across the monorepo workspaces:

| Agent | Workspace | Domain & Responsibilities | Key Verification Deliverable |
|---|---|---|---|
| **Agent-01-QuantCore** | `services/kronos-embedder/` | Kronos model wrapping, strict causal normalization, recency attention pooling, `/embed` and `/predict-cone` endpoints | PyTest benchmark verifying zero lookahead leakage & $<18\text{ms}$ inference |
| **Agent-02-VectorOps** | `services/ingestion-worker/` & `services/api/` | TimescaleDB schemas, Qdrant HNSW int8 tuning, multi-asset ingestion worker, `/api/v1/search-pattern` endpoint | Load-test proving $<35\text{ms}$ p95 ANN search and temporal leakage filters |
| **Agent-03-TerminalUI** | `apps/web/` | Next.js 15, TradingView Lightweight Charts custom canvas primitive, brush tool, Reality Cone fan, twin carousel | Interactive UI canvas rendering Reality Cone in $<150\text{ms}$ |
| **Agent-04-GrowthEngine** | `apps/web/src/growth/` & `services/growth-bot/` | Dynamic 1200x630 OpenGraph cards (`/api/og/cone`), 1-click share to X, embeddable broker widgets, macro volatility bot | Visual social cards & embeddable iframe test suite |

---

## 3. Mathematical Foundations & Algorithms

### 3.1 Strict Causal Instance Normalization
To guarantee zero lookahead leakage, raw OHLCV+Amount arrays $W_{t-L+1:t} \in \mathbb{R}^{L \times 6}$ are normalized strictly within the rolling window before entering the tokenizer:
$$\mu_{\text{price}} = \frac{1}{4L}\sum_{\tau=1}^L (O_\tau + H_\tau + L_\tau + C_\tau), \quad \sigma_{\text{price}} = \sqrt{\frac{1}{4L}\sum_{\tau=1}^L (P_\tau - \mu_{\text{price}})^2} + \epsilon$$
$$\tilde{V}_\tau = \frac{\log(1 + V_\tau) - \mu_{\text{vol}}}{\sigma_{\text{vol}} + \epsilon}$$

### 3.2 Recency-Weighted Attention Pooling
Breakout geometry is concentrated in the tail of the selected window. We apply a linear recency-weighting kernel to the causal transformer's hidden representations $H \in \mathbb{R}^{L \times d_{\text{model}}}$:
$$w_\tau = 0.5 + 1.0 \times \frac{\tau - 1}{L - 1}, \quad \tau \in [1, L]$$
$$\mathbf{e}_{\text{raw}} = \frac{\sum_{\tau=1}^L w_\tau H_\tau}{\sum_{\tau=1}^L w_\tau}, \quad \mathbf{e} = \frac{\mathbf{e}_{\text{raw}}}{\|\mathbf{e}_{\text{raw}}\|_2}$$

### 3.3 Hybrid Reality Cone Ensemble
Given a brushed live pattern $\mathbf{x}_{\text{live}}$:
1. **Empirical Historical Distribution ($P_{\text{hist}}$)**: Retrieve top $K=100$ analogs from Qdrant with $d_{\text{cosine}} \ge 0.82$, filtering out contemporaneous timestamps $[T_{\text{now}} - L, T_{\text{now}}]$. Extract normalized forward return paths $R_k(t)$ for $t \in [1, 20]$.
2. **Generative Foundation Distribution ($P_{\text{gen}}$)**: Autoregressively sample $M=100$ forward paths $G_m(t)$ using temperature $T=1.0$ and nucleus sampling $\text{top\_p}=0.90$.
3. **Bayesian Ensemble**: Combine $P_{\text{hist}}$ and $P_{\text{gen}}$ into empirical quantiles $Q_\alpha(t)$ for $\alpha \in \{0.10, 0.25, 0.50, 0.75, 0.90\}$, compute the empirical win rate (% positive at bar $+10$ and $+20$), and calculate the median risk-to-reward ratio.

---

## 4. Monorepo Directory Structure

```
xpredictor/
├── .antigravity/
│   ├── project.json              # Antigravity 2.0 monorepo configuration
│   ├── rules.md                  # Strict quantitative and anti-leakage guardrails
│   └── agents/                   # Agent prompts and operational scopes
│       ├── Agent-01-QuantCore.md
│       ├── Agent-02-VectorOps.md
│       ├── Agent-03-TerminalUI.md
│       └── Agent-04-GrowthEngine.md
├── apps/
│   └── web/                      # Next.js 15 Financial Canvas Terminal
│       ├── package.json
│       ├── tsconfig.json
│       └── src/
│           ├── app/              # App router (main terminal, embed, og route)
│           ├── components/       # Canvas brush, Reality Cone, Carousel, Scorecard
│           └── growth/           # OpenGraph card generator & share modules
├── services/
│   ├── kronos-embedder/          # Kronos foundation model wrapping service
│   │   ├── extractor.py          # KronosPatternEngine with causal pooling
│   │   ├── main.py               # FastAPI embedding & cone endpoints
│   │   └── test_lookahead.py     # Verification tests for zero lookahead leakage
│   ├── api/                      # Gateway & Reality Cone orchestration service
│   │   ├── main.py               # /api/v1/search-pattern & metrics aggregation
│   │   ├── routers/              # Search, tickers, and embed endpoints
│   │   └── test_search_api.py    # Search verification tests
│   ├── ingestion-worker/         # Async multi-asset market ingestion pipeline
│   │   ├── worker.py             # Rolling window generator & Qdrant upsert
│   │   └── pipeline.py           # Multi-exchange data loaders
│   └── growth-bot/               # Automated macro catalyst Twitter/Reddit bot
│       └── bot.py                # Volatility detector & card publisher
├── infra/
│   └── docker/
│       ├── docker-compose.yml    # Qdrant (v1.11+), TimescaleDB (pg16), Redis (v7)
│       └── qdrant_init.py        # HNSW & int8 scalar quantization provisioning
└── README.md                     # Comprehensive project documentation
```

---

## 5. Go-To-Market (GTM) & Monetization

1. **Top-of-Funnel Lead Magnet**: Rebrand `aigoldforecast.com` as "Powered by XPredictor" offering free 3-analog scans on daily gold charts with CTAs leading directly into the XPredictor terminal.
2. **Viral Catalyst Hijack Engine**: Automated publishing of high-conviction historical twin comparisons on X/Twitter and Reddit during high-volatility catalysts (CPI, FOMC, NFP, breakouts).
3. **Embeddable Widgets (Product-Led Growth)**: Provide 1-click embed code for Substack and Beehiiv financial newsletters with embedded 30% affiliate revenue sharing.
4. **B2B White-Label Licensing**: Embeddable pattern search widgets for retail brokers (Zerodha, Dhan, Bybit, Exness) priced at \$2,500–\$7,500/month.
