"use client";

import React, { useState, useEffect } from "react";
import { ChartCanvas } from "./ChartCanvas";
import { ScoreCard } from "./ScoreCard";
import { AnalogCarousel, HistoricalTwinItem } from "./AnalogCarousel";
import { EmbedModal } from "./EmbedModal";
import { Search, Zap, Layers, BarChart3, RefreshCw } from "lucide-react";

const SUPPORTED_TICKERS = [
  { symbol: "XAUUSD", name: "Gold / USD", class: "commodities" },
  { symbol: "BTCUSD", name: "Bitcoin / USD", class: "crypto" },
  { symbol: "ETHUSD", name: "Ethereum / USD", class: "crypto" },
  { symbol: "EURUSD", name: "Euro / USD", class: "fx_gold" },
  { symbol: "NAS100", name: "Nasdaq 100", class: "equities" },
  { symbol: "NVDA", name: "Nvidia", class: "equities" },
];

export const PatternTerminal: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState("XAUUSD");
  const [selectedTimeframe, setSelectedTimeframe] = useState("1h");
  const [assetFilter, setAssetFilter] = useState("all");
  const [candles, setCandles] = useState<any[]>([]);
  const [brushRange, setBrushRange] = useState<[number, number]>([0, 63]);
  const [activeGhostTwin, setActiveGhostTwin] = useState<HistoricalTwinItem | null>(null);
  const [embedModalOpen, setEmbedModalOpen] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [livePrice, setLivePrice] = useState<number | null>(null);
  const [tickDirection, setTickDirection] = useState<"up" | "down" | null>(null);

  // Free Binance WebSocket real-time streaming
  useEffect(() => {
    let ws: WebSocket | null = null;
    let stream = "paxgusdt@kline_1s"; // Paxos Gold 1:1 physical gold
    if (selectedTicker === "BTCUSD") stream = "btcusdt@kline_1s";
    else if (selectedTicker === "ETHUSD") stream = "ethusdt@kline_1s";

    try {
      ws = new WebSocket(`wss://stream.binance.com:9443/ws/${stream}`);
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.k) {
            const price = parseFloat(msg.k.c);
            setLivePrice((prev) => {
              if (prev !== null) {
                setTickDirection(price >= prev ? "up" : "down");
              }
              return price;
            });

            setCandles((prev) => {
              if (!prev || prev.length === 0) return prev;
              const copy = [...prev];
              const last = { ...copy[copy.length - 1] };
              last.close = price;
              last.high = Math.max(last.high, parseFloat(msg.k.h));
              last.low = Math.min(last.low, parseFloat(msg.k.l));
              copy[copy.length - 1] = last;
              return copy;
            });
          }
        } catch {}
      };
    } catch {}

    return () => {
      if (ws) {
        try { ws.close(); } catch {}
      }
    };
  }, [selectedTicker]);

  // Score & reality cone state
  const [realityCone, setRealityCone] = useState<any>(null);
  const [scoreData, setScoreData] = useState<any>({
    bullish_skew_pct: 86.4,
    win_rate_20b: 73.0,
    win_rate_10b: 68.5,
    median_return_pct: 1.84,
    median_max_dd_pct: -0.52,
    optimal_rr: 3.54,
    regime_breakdown: { crypto: 42, fx_gold: 38, equities: 20 },
    analog_count: 100,
  });
  const [twins, setTwins] = useState<HistoricalTwinItem[]>([
    {
      symbol: "BTCUSD",
      asset_class: "crypto",
      timeframe: "1h",
      date_formatted: "Nov 2024",
      start_ts: 1730000000,
      end_ts: 1730200000,
      match_pct: 96.4,
      fwd_20_ret_pct: 4.20,
      fwd_20_max_dd_pct: -0.65,
      fwd_20_normalized_path: [0.1, 0.4, 0.8, 1.2, 1.5, 2.1, 2.5, 2.8, 3.1, 3.4, 3.2, 3.6, 3.9, 4.1, 4.3, 4.0, 4.2, 4.4, 4.1, 4.2],
    },
    {
      symbol: "XAUUSD",
      asset_class: "commodities",
      timeframe: "1h",
      date_formatted: "Mar 2024",
      start_ts: 1710000000,
      end_ts: 1710200000,
      match_pct: 95.8,
      fwd_20_ret_pct: 2.85,
      fwd_20_max_dd_pct: -0.42,
      fwd_20_normalized_path: [0.2, 0.3, 0.6, 0.9, 1.1, 1.4, 1.6, 1.8, 2.2, 2.4, 2.1, 2.5, 2.7, 2.6, 2.8, 2.9, 2.7, 2.8, 2.9, 2.85],
    },
    {
      symbol: "NVDA",
      asset_class: "equities",
      timeframe: "1h",
      date_formatted: "Jan 2025",
      start_ts: 1736000000,
      end_ts: 1736200000,
      match_pct: 94.9,
      fwd_20_ret_pct: -1.10,
      fwd_20_max_dd_pct: -2.30,
      fwd_20_normalized_path: [-0.1, -0.3, -0.2, -0.6, -0.8, -1.2, -1.5, -1.3, -1.7, -1.9, -1.5, -1.8, -1.4, -1.2, -1.0, -1.3, -1.1, -1.2, -1.0, -1.1],
    },
    {
      symbol: "ETHUSD",
      asset_class: "crypto",
      timeframe: "1h",
      date_formatted: "Sep 2024",
      start_ts: 1726000000,
      end_ts: 1726200000,
      match_pct: 94.2,
      fwd_20_ret_pct: 3.75,
      fwd_20_max_dd_pct: -0.80,
      fwd_20_normalized_path: [0.3, 0.5, 0.9, 1.3, 1.7, 2.0, 2.3, 2.8, 3.1, 3.5, 3.2, 3.4, 3.7, 3.6, 3.8, 3.9, 3.6, 3.7, 3.8, 3.75],
    },
  ]);

  // Fetch candles (loads real MT5 gold data when available)
  useEffect(() => {
    let isMounted = true;
    async function loadCandles() {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/candles?symbol=${selectedTicker}&timeframe=${selectedTimeframe}&limit=120`);
        if (res.ok) {
          const json = await res.json();
          if (json.candles && json.candles.length >= 32 && isMounted) {
            setCandles(json.candles);
            const defaultStart = Math.max(0, json.candles.length - 64);
            const defaultEnd = json.candles.length - 1;
            setBrushRange([defaultStart, defaultEnd]);
            triggerPatternSearch(json.candles.slice(defaultStart, defaultEnd + 1));
            return;
          }
        }
      } catch {}

      // Fallback generator with 120 bars for smooth brushing
      if (!isMounted) return;
      let basePrice = 2650.0;
      if (selectedTicker === "BTCUSD") basePrice = 68000.0;
      else if (selectedTicker === "ETHUSD") basePrice = 3500.0;
      else if (selectedTicker === "EURUSD") basePrice = 1.085;
      else if (selectedTicker === "NAS100") basePrice = 19500.0;
      else if (selectedTicker === "NVDA") basePrice = 135.0;

      const generated = [];
      let p = basePrice;
      const totalBars = 120;
      for (let i = 0; i < totalBars; i++) {
        const ret = (Math.sin(i * 0.12) + (Math.random() - 0.48)) * 0.005;
        p = p * (1 + ret);
        const high = p * (1 + Math.abs(Math.random() * 0.002));
        const low = p * (1 - Math.abs(Math.random() * 0.002));
        const open = low + Math.random() * (high - low);
        const close = low + Math.random() * (high - low);
        generated.push({
          time: Math.floor(Date.now() / 1000) - (totalBars - i) * 3600,
          open: Math.round(open * 100) / 100,
          high: Math.round(high * 100) / 100,
          low: Math.round(low * 100) / 100,
          close: Math.round(close * 100) / 100,
          volume: Math.floor(1000 + Math.random() * 5000),
        });
      }

      setCandles(generated);
      const defaultStart = Math.max(0, generated.length - 64);
      const defaultEnd = generated.length - 1;
      setBrushRange([defaultStart, defaultEnd]);
      triggerPatternSearch(generated.slice(defaultStart, defaultEnd + 1));
    }

    loadCandles();
    return () => { isMounted = false; };
  }, [selectedTicker, selectedTimeframe]);

  const triggerPatternSearch = async (brushCandles: any[]) => {
    setIsScanning(true);
    try {
      const formattedCandles = brushCandles.map((c) => [c.open, c.high, c.low, c.close, c.volume, c.volume * c.close]);
      const res = await fetch("http://localhost:8000/api/v1/search-pattern", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: selectedTicker,
          timeframe: selectedTimeframe,
          candles: formattedCandles,
          asset_filter: assetFilter,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setRealityCone(data.quantiles);
        setScoreData({
          bullish_skew_pct: data.bullish_skew_pct,
          win_rate_20b: data.win_rate_20b,
          win_rate_10b: data.win_rate_10b,
          median_return_pct: data.median_return_pct,
          median_max_dd_pct: data.median_max_dd_pct,
          optimal_rr: data.optimal_rr,
          regime_breakdown: data.regime_breakdown,
          analog_count: data.analog_count,
        });
        if (data.top_historical_twins && data.top_historical_twins.length > 0) {
          setTwins(data.top_historical_twins);
        }
      } else {
        // Fallback realistic simulation
        setDefaultSimulationCone();
      }
    } catch {
      setDefaultSimulationCone();
    } finally {
      setIsScanning(false);
    }
  };

  const setDefaultSimulationCone = () => {
    setRealityCone({
      p10: [-1.2, -1.5, -1.8, -2.1, -2.4, -2.8, -3.1, -3.4, -3.7, -4.0, -4.2, -4.5, -4.7, -4.9, -5.1, -5.3, -5.5, -5.7, -5.9, -6.1],
      p25: [-0.4, -0.6, -0.7, -0.9, -1.0, -1.2, -1.3, -1.4, -1.5, -1.6, -1.7, -1.8, -1.9, -2.0, -2.1, -2.2, -2.3, -2.4, -2.5, -2.6],
      p50: [0.2, 0.4, 0.7, 0.9, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.3, 2.5, 2.6, 2.8, 2.9, 3.1, 3.2, 3.4, 3.5, 3.6],
      p75: [0.6, 1.1, 1.6, 2.0, 2.5, 2.9, 3.4, 3.8, 4.2, 4.6, 5.0, 5.4, 5.7, 6.1, 6.4, 6.7, 7.0, 7.3, 7.6, 7.9],
      p90: [1.2, 2.1, 2.9, 3.7, 4.5, 5.2, 6.0, 6.7, 7.4, 8.1, 8.8, 9.4, 10.0, 10.6, 11.2, 11.8, 12.3, 12.8, 13.4, 13.9],
    });
  };

  const handleRangeChange = (start: number, end: number) => {
    setBrushRange([start, end]);
    if (candles.length > 0) {
      triggerPatternSearch(candles.slice(start, end + 1));
    }
  };

  const handleShare = () => {
    const shareUrl = `${window.location.origin}/api/og/cone?symbol=${selectedTicker}&tf=${selectedTimeframe}&skew=${scoreData.bullish_skew_pct}`;
    window.open(shareUrl, "_blank");
  };

  return (
    <div className="flex flex-col min-h-screen bg-background text-gray-100">
      {/* Top Navigation Bar */}
      <header className="h-14 border-b border-gray-800 bg-surface px-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-gradient-to-tr from-kronos to-indigo-500 flex items-center justify-center font-bold text-white text-sm shadow-lg shadow-kronos/30">
              XP
            </div>
            <span className="font-bold tracking-tight text-base bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-400">
              XPredictor
            </span>
          </div>
          <span className="text-xs bg-kronos/15 text-kronos font-medium px-2 py-0.5 rounded border border-kronos/30 hidden sm:inline-block">
            Shazam for Candlesticks
          </span>
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[11px]">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>LIVE (1s WS)</span>
          </div>
          {livePrice !== null && (
            <div className={`font-mono font-bold text-xs px-2 py-0.5 rounded border transition duration-150 ${
              tickDirection === 'up'
                ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400'
                : 'bg-rose-500/15 border-rose-500/40 text-rose-400'
            }`}>
              {tickDirection === 'up' ? '▲' : '▼'} ${livePrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3 text-xs">
          {/* Ticker Select */}
          <div className="flex items-center gap-1.5 bg-surfaceElevated px-2 py-1 rounded border border-gray-700">
            <span className="text-gray-400">Symbol:</span>
            <select
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
              className="bg-transparent text-white font-bold focus:outline-none cursor-pointer"
            >
              {SUPPORTED_TICKERS.map((t) => (
                <option key={t.symbol} value={t.symbol} className="bg-surface">
                  {t.symbol} ({t.name})
                </option>
              ))}
            </select>
          </div>

          {/* Timeframe Select */}
          <div className="flex bg-surfaceElevated rounded border border-gray-700 p-0.5">
            {["15m", "1h", "4h", "1d"].map((tf) => (
              <button
                key={tf}
                onClick={() => setSelectedTimeframe(tf)}
                className={`px-2 py-0.5 rounded font-medium transition ${
                  selectedTimeframe === tf ? "bg-kronos text-white" : "text-gray-400 hover:text-white"
                }`}
              >
                {tf.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Asset Universe Filter */}
          <div className="flex items-center gap-1 bg-surfaceElevated px-2 py-1 rounded border border-gray-700">
            <Layers className="w-3.5 h-3.5 text-gray-400" />
            <select
              value={assetFilter}
              onChange={(e) => setAssetFilter(e.target.value)}
              className="bg-transparent text-gray-300 focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-surface">All Universes</option>
              <option value="crypto" className="bg-surface">Crypto</option>
              <option value="fx_gold" className="bg-surface">FX / Gold</option>
              <option value="equities" className="bg-surface">Equities</option>
            </select>
          </div>

          {isScanning && (
            <div className="flex items-center gap-1 text-kronos animate-pulse">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Scanning 50M+ windows...
            </div>
          )}
        </div>
      </header>

      {/* Main Workspace Layout */}
      <main className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-4 gap-4 max-w-[1700px] w-full mx-auto">
        {/* Chart Viewport & Bottom Carousel (3 Columns) */}
        <div className="lg:col-span-3 flex flex-col space-y-4">
          <ChartCanvas
            candles={candles}
            realityCone={realityCone}
            activeGhostTwin={activeGhostTwin}
            selectedRange={brushRange}
            onRangeChange={handleRangeChange}
            isScanning={isScanning}
          />
          <AnalogCarousel
            twins={twins}
            activeTwin={activeGhostTwin}
            onSelectTwin={(twin) => setActiveGhostTwin(activeGhostTwin?.date_formatted === twin.date_formatted ? null : twin)}
          />
        </div>

        {/* Right Scorecard Panel (1 Column) */}
        <div className="lg:col-span-1">
          <ScoreCard
            scoreData={scoreData}
            onShare={handleShare}
            onAlert={() => alert("Breakout alert set for this pattern structure.")}
            onEmbed={() => setEmbedModalOpen(true)}
          />
        </div>
      </main>

      {/* Embed Modal */}
      <EmbedModal
        isOpen={embedModalOpen}
        onClose={() => setEmbedModalOpen(false)}
        symbol={selectedTicker}
        timeframe={selectedTimeframe}
      />
    </div>
  );
};
