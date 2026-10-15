# Global Antigravity Agent Guardrails

All Antigravity autonomous agents operating in the `xpredictor` monorepo must adhere strictly to these quantitative, algorithmic, and engineering standards:

## 1. Strict Causal Normalization (Zero Lookahead Leakage)
Never normalize a historical K-line window using global dataset statistics or future price bars. Every rolling window $W_{t-L+1:t}$ of length $L \in \{32, 64, 128\}$ must be instance-normalized strictly using its own local window mean $\mu_W$ and standard deviation $\sigma_W$ prior to entering `KronosTokenizer`.
$$\tilde{P}_i = \frac{P_i - \mu_{\text{price}}}{\sigma_{\text{price}} + \epsilon}, \quad \tilde{V}_i = \frac{\log(1 + V_i) - \mu_{\text{vol}}}{\sigma_{\text{vol}} + \epsilon}$$
No post-window data, forward indicators, or future session ranges may bleed into the feature tensors.

## 2. Exclude Forward Leakage in Vector Retrieval
When querying Qdrant for a live pattern on ticker $S$ at timestamp $T_{\text{now}}$, the query engine must apply a mandatory payload filter excluding any historical window from ticker $S$ whose timestamp overlaps $[T_{\text{now}} - L, T_{\text{now}}]$. Live patterns must never match against themselves or their immediate antecedents within the lookback window.

## 3. Artifact-First Deliverables
Every agent task must produce an Antigravity Artifact (unit test execution log, latency benchmark report, or interactive UI preview recording) before marking a task complete and merging changes into `main`.

## 4. Sub-20ms Embedding & Sub-35ms ANN Retrieval Latency Budgets
- `services/kronos-embedder`: Single-window 768-D embedding extraction must complete in $\le 18\text{ms}$ on GPU and $\le 25\text{ms}$ in optimized ONNX/TensorRT mode.
- `services/api`: Top-100 Approximate Nearest Neighbor (ANN) vector retrieval across 50M+ vectors in Qdrant must achieve p95 latency $\le 35\text{ms}$.
- End-to-end brush-to-cone response time from UI canvas release to reality cone rendering must stay below $150\text{ms}$.

## 5. Regulatory Safe-Harbor Positioning
Never position or label XPredictor as an "AI Buy/Sell Signal Generator". Position it strictly as a **"Quantitative Historical Pattern Search & Statistical Distribution Research Terminal"**. Analog discovery and quantile fan cones represent mathematical data analytics (analogous to Bloomberg GP or TradingView indicators) to prevent CTA/RIA licensing entanglements.
