# Agent-01-QuantCore

**Workspace**: `services/kronos-embedder/`
**Role**: Quantitative Foundation Model Engineer

## Primary Responsibilities
1. Wrap `shiyu-coder/Kronos` (`NeoQuasar/Kronos-Tokenizer-base` and `NeoQuasar/Kronos-base`).
2. Extract multi-scale latent pooled hidden states ($d_{\text{model}} = 768$) alongside hierarchical token sequences.
3. Enforce strict causal per-window instance normalization: zero future information leakage.
4. Apply recency-weighted attention pooling over the sequence dimension to emphasize the breakout tail:
   ```python
   weights = torch.linspace(0.5, 1.5, steps=seq_len, device=device).view(1, seq_len, 1)
   pooled = (hidden_states * weights).sum(dim=1) / weights.sum(dim=1)
   embedding = F.normalize(pooled, p=2, dim=-1)
   ```
5. Serve high-throughput FastAPI endpoints:
   - `POST /embed`: Accepts batch of `(N, L, 6)` OHLCV windows, returns L2-normalized 768-D vectors.
   - `POST /predict-cone`: Runs `KronosPredictor.predict(sample_count=100, T=1.0, top_p=0.90)` and returns the 10th, 25th, 50th, 75th, and 90th percentile forward trajectories.

## Verification Artifact Required
PyTest benchmark suite verifying $<18\text{ms}$ single-window embedding latency on GPU and mathematically proven zero lookahead leakage on rolling z-score normalization.
