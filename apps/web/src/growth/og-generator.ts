/**
 * apps/web/src/growth/og-generator.ts
 * Generates dynamic SVG / OpenGraph social preview cards (1200x630).
 */

export interface OGCardOptions {
  symbol: string;
  timeframe: string;
  bullishSkew: number;
  matchDate: string;
  matchPct: number;
  winRate: number;
  optimalRR: number;
}

export function generateOGCardSvg(options: OGCardOptions): string {
  const isBullish = options.bullishSkew >= 50;
  const statusColor = isBullish ? "#10B981" : "#F43F5E";

  return `
  <svg width="1200" height="630" viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#090D16" />
        <stop offset="100%" stop-color="#111827" />
      </linearGradient>
      <linearGradient id="coneGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.1" />
        <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0.5" />
      </linearGradient>
    </defs>

    <!-- Background -->
    <rect width="1200" height="630" fill="url(#bg)" />

    <!-- Border Accent -->
    <rect x="2" y="2" width="1196" height="626" rx="12" fill="none" stroke="#1F2937" stroke-width="4" />

    <!-- Header Logo & Watermark -->
    <rect x="60" y="50" width="44" height="44" rx="8" fill="#8B5CF6" />
    <text x="73" y="80" font-family="sans-serif" font-weight="bold" font-size="22" fill="#FFFFFF">XP</text>
    <text x="120" y="82" font-family="sans-serif" font-weight="bold" font-size="28" fill="#F3F4F6">XPredictor</text>
    <text x="270" y="82" font-family="sans-serif" font-size="18" fill="#8B5CF6">| Shazam for Candlesticks</text>
    <text x="1000" y="82" font-family="monospace" font-size="20" fill="#6B7280">xpredictor.com</text>

    <!-- Main Title Banner -->
    <text x="60" y="160" font-family="sans-serif" font-weight="bold" font-size="44" fill="#FFFFFF">
      ${options.symbol} (${options.timeframe.toUpperCase()}) Setup Analysis
    </text>

    <!-- Core Stat Cards -->
    <rect x="60" y="200" width="340" height="150" rx="10" fill="#1F2937" stroke="#374151" stroke-width="1.5" />
    <text x="80" y="240" font-family="sans-serif" font-size="16" fill="#9CA3AF">ANALOG SKEW SCORE</text>
    <text x="80" y="300" font-family="sans-serif" font-weight="bold" font-size="40" fill="${statusColor}">
      ${options.bullishSkew}% ${isBullish ? "BULLISH" : "BEARISH"}
    </text>

    <rect x="430" y="200" width="340" height="150" rx="10" fill="#1F2937" stroke="#374151" stroke-width="1.5" />
    <text x="450" y="240" font-family="sans-serif" font-size="16" fill="#9CA3AF">WIN RATE (+20 BARS)</text>
    <text x="450" y="300" font-family="monospace" font-weight="bold" font-size="40" fill="#F3F4F6">
      ${options.winRate}%
    </text>

    <rect x="800" y="200" width="340" height="150" rx="10" fill="#1F2937" stroke="#374151" stroke-width="1.5" />
    <text x="820" y="240" font-family="sans-serif" font-size="16" fill="#9CA3AF">OPTIMAL REWARD:RISK</text>
    <text x="820" y="300" font-family="monospace" font-weight="bold" font-size="40" fill="#8B5CF6">
      ${options.optimalRR}x
    </text>

    <!-- Nearest Twin Box -->
    <rect x="60" y="380" width="1080" height="180" rx="10" fill="#1F2937" stroke="#8B5CF6" stroke-width="2" />
    <text x="90" y="425" font-family="sans-serif" font-weight="bold" font-size="20" fill="#8B5CF6">
      #1 Closest Historical Twin:
    </text>
    <text x="350" y="425" font-family="sans-serif" font-size="20" fill="#FFFFFF">
      ${options.symbol} (${options.matchDate}) - ${options.matchPct}% Structural Vector Match
    </text>

    <!-- Simulated Cone Visual Graphic -->
    <path d="M 90 510 Q 600 480 1050 430 L 1050 530 Q 600 520 90 510 Z" fill="url(#coneGrad)" />
    <line x1="90" y1="510" x2="1050" y2="475" stroke="#A78BFA" stroke-width="3" />

    <!-- Footer Tagline -->
    <text x="60" y="600" font-family="sans-serif" font-size="14" fill="#9CA3AF">
      Computed across 50,000,000+ multi-asset candlestick windows using Kronos foundation embeddings.
    </text>
  </svg>
  `;
}
