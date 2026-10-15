# Agent-03-TerminalUI

**Workspace**: `apps/web/`
**Role**: High-Frequency Web UI & Financial Canvas Engineer

## Primary Responsibilities
1. Scaffold and develop Next.js 15 (App Router, React 19, TypeScript) client application.
2. Financial charting engine:
   - TradingView `lightweight-charts` (v4.2+) integrated with custom HTML5 Canvas primitive (`ISeriesPrimitive`) for:
     - Shift+Drag Candlestick Brush (selecting 32 to 128 candles dynamically).
     - Hybrid Reality Cone overlay (10th, 25th, 50th, 75th, 90th percentile fan with semi-transparent violet shading).
3. State management & synchronization:
   - TanStack Query v5 + Zustand for zero-flicker state and synchronized cross-chart analog replay.
4. Signature micro-interactions:
   - **Click-and-Drag "Shazam" Brush**: Instant search invocation without form submissions.
   - **Ghost Analog Replay Slider**: Overlaying historical twin candles as semi-transparent gold ghost candles onto the live chart.
   - **Top Historical Twins Carousel**: Interactive cards displaying symbol, timestamp, cosine match %, and 20-bar forward outcome.
   - **Historical Analog Scoreboard**: Win rate (+20b), median return, max DD, optimal R:R, and regime breakdown (Crypto, FX/Gold, Equity).

## Verification Artifact Required
Antigravity Browser Preview artifact demonstrating interactive 50-bar brush selection rendering the Reality Cone in $<150\text{ms}$ end-to-end.
