# Agent-04-GrowthEngine

**Workspace**: `apps/web/src/growth/` & `services/growth-bot/`
**Role**: Product-Led Growth & Viral Distribution Architect

## Primary Responsibilities
1. Social Proof & Viral Generators:
   - Dynamic 1200x630 OpenGraph card generation route (`/api/og/cone?id=...` via `@vercel/og` / Canvas).
   - Instant 1-Click "Share Reality Cone to X/TradingView/Reddit" flow featuring branded cards, domain watermark, ticker, top 3 twins, and statistical quantiles.
2. Embeddable B2B Broker / Newsletter Widgets:
   - Embed route (`/embed/[symbol]/[timeframe]`) allowing clean `<iframe>` embedding for Substack, Beehiiv, Discord bots, and broker partner portals.
   - Built-in affiliate tracking parameter (`?ref=user_id`) enabling 30% recurring creator revenue share.
3. Automated "Macro Event Live-Twin" Hijack Bot:
   - Service in `services/growth-bot/bot.py` monitoring high-volatility catalysts (CPI, FOMC, NFP, breakouts).
   - Generates high-converting data cards with precise empirical twin dates and verifiable statistics (e.g. "96.2% match with Oct 18, 2024; price swept high in 6 bars 78% of time before mean-reverting -1.4%").

## Verification Artifact Required
Rendered 1200x630 OpenGraph social preview artifact, embed iframe validator, and automated catalyst tweet generator test log.
