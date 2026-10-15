"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { HistoricalTwinItem } from "./AnalogCarousel";
import { MousePointer, Sparkles, CheckCircle2 } from "lucide-react";

interface CandlestickData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface ChartCanvasProps {
  candles: CandlestickData[];
  realityCone: {
    p10: number[];
    p25: number[];
    p50: number[];
    p75: number[];
    p90: number[];
  } | null;
  activeGhostTwin: HistoricalTwinItem | null;
  selectedRange: [number, number]; // [startIndex, endIndex]
  onRangeChange: (start: number, end: number) => void;
  isScanning?: boolean;
}

export const ChartCanvas: React.FC<ChartCanvasProps> = ({
  candles,
  realityCone,
  activeGhostTwin,
  selectedRange,
  onRangeChange,
  isScanning = false,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Drag interaction state
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartIdx, setDragStartIdx] = useState<number | null>(null);
  const [dragCurrentIdx, setDragCurrentIdx] = useState<number | null>(null);

  // Quick preset helper
  const applyPreset = (barCount: number) => {
    if (candles.length === 0) return;
    const end = candles.length - 1;
    const start = Math.max(0, end - barCount + 1);
    onRangeChange(start, end);
  };

  // Convert mouse coordinate X to candle index
  const getIndexFromX = useCallback((clientX: number): number => {
    const canvas = canvasRef.current;
    if (!canvas || candles.length === 0) return 0;
    const rect = canvas.getBoundingClientRect();
    const x = clientX - rect.left;
    const candleWidth = Math.max(4, (rect.width - 120) / (candles.length + 22));
    const idx = Math.floor(x / candleWidth);
    return Math.max(0, Math.min(candles.length - 1, idx));
  }, [candles.length]);

  // Handle Mouse Down
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const idx = getIndexFromX(e.clientX);
    setIsDragging(true);
    setDragStartIdx(idx);
    setDragCurrentIdx(idx);
  };

  // Handle Mouse Move
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging || dragStartIdx === null) return;
    const idx = getIndexFromX(e.clientX);
    setDragCurrentIdx(idx);
  };

  // Handle Mouse Up
  const handleMouseUp = useCallback(() => {
    if (!isDragging || dragStartIdx === null || dragCurrentIdx === null) {
      setIsDragging(false);
      setDragStartIdx(null);
      setDragCurrentIdx(null);
      return;
    }

    let start = Math.min(dragStartIdx, dragCurrentIdx);
    let end = Math.max(dragStartIdx, dragCurrentIdx);
    let count = end - start + 1;

    // Enforce valid window constraints [32, 128]
    if (count < 32) {
      // Auto-expand to minimum 32 bars anchored to selection
      if (end + (32 - count) < candles.length) {
        end += (32 - count);
      } else if (start - (32 - count) >= 0) {
        start -= (32 - count);
      } else {
        start = 0;
        end = Math.min(candles.length - 1, 31);
      }
    } else if (count > 128) {
      end = start + 127;
    }

    setIsDragging(false);
    setDragStartIdx(null);
    setDragCurrentIdx(null);
    onRangeChange(start, end);
  }, [isDragging, dragStartIdx, dragCurrentIdx, candles.length, onRangeChange]);

  // Window-level mouseup listener for smooth release outside canvas
  useEffect(() => {
    const onWindowMouseUp = () => {
      if (isDragging) {
        handleMouseUp();
      }
    };
    window.addEventListener("mouseup", onWindowMouseUp);
    return () => window.removeEventListener("mouseup", onWindowMouseUp);
  }, [isDragging, handleMouseUp]);

  // Canvas Rendering
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.parentElement?.clientWidth || 800;
    const height = 480;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // Background
    ctx.fillStyle = "#090D16";
    ctx.fillRect(0, 0, width, height);

    if (candles.length === 0) return;

    // Price scaling
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    candles.forEach((c) => {
      minPrice = Math.min(minPrice, c.low);
      maxPrice = Math.max(maxPrice, c.high);
    });

    const pricePadding = (maxPrice - minPrice) * 0.16;
    minPrice -= pricePadding;
    maxPrice += pricePadding;

    const candleWidth = Math.max(4, (width - 120) / (candles.length + 22));
    const priceToY = (p: number) => height - 40 - ((p - minPrice) / (maxPrice - minPrice)) * (height - 80);

    // 1. Grid & Price Labels
    ctx.strokeStyle = "#1F2937";
    ctx.lineWidth = 1;
    for (let i = 1; i <= 5; i++) {
      const y = (height / 6) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width - 70, y);
      ctx.stroke();

      const priceLevel = maxPrice - ((y - 40) / (height - 80)) * (maxPrice - minPrice);
      ctx.fillStyle = "#6B7280";
      ctx.font = "10px monospace";
      ctx.fillText(priceLevel.toFixed(2), width - 65, y + 3);
    }

    // 2. Active Selection or In-Progress Drag Box
    let activeStart = selectedRange[0];
    let activeEnd = selectedRange[1];

    if (isDragging && dragStartIdx !== null && dragCurrentIdx !== null) {
      activeStart = Math.min(dragStartIdx, dragCurrentIdx);
      activeEnd = Math.max(dragStartIdx, dragCurrentIdx);
    }

    if (activeStart >= 0 && activeEnd < candles.length) {
      const brushX = activeStart * candleWidth;
      const brushW = (activeEnd - activeStart + 1) * candleWidth;
      const barCount = activeEnd - activeStart + 1;

      // Fill
      ctx.fillStyle = isDragging ? "rgba(139, 92, 246, 0.25)" : "rgba(139, 92, 246, 0.15)";
      ctx.fillRect(brushX, 20, brushW, height - 60);

      // Border
      ctx.strokeStyle = "#8B5CF6";
      ctx.lineWidth = isDragging ? 2.0 : 1.5;
      if (!isDragging) ctx.setLineDash([4, 4]);
      ctx.strokeRect(brushX, 20, brushW, height - 60);
      ctx.setLineDash([]);

      // Top Header Badge on selection box
      ctx.fillStyle = "#8B5CF6";
      ctx.beginPath();
      ctx.roundRect(brushX, 20, Math.min(brushW, 140), 22, [0, 0, 4, 0]);
      ctx.fill();

      ctx.fillStyle = "#FFFFFF";
      ctx.font = "bold 11px sans-serif";
      const badgeText = isDragging ? `Brushing ${barCount} Bars` : `Pattern Window: ${barCount}b`;
      ctx.fillText(badgeText, brushX + 6, 35);
    }

    // 3. Draw Candlesticks
    candles.forEach((c, idx) => {
      const x = idx * candleWidth + candleWidth / 2;
      const openY = priceToY(c.open);
      const closeY = priceToY(c.close);
      const highY = priceToY(c.high);
      const lowY = priceToY(c.low);

      const isUp = c.close >= c.open;
      const candleColor = isUp ? "#10B981" : "#F43F5E";

      // Wick
      ctx.strokeStyle = candleColor;
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(x, highY);
      ctx.lineTo(x, lowY);
      ctx.stroke();

      // Body
      ctx.fillStyle = candleColor;
      const bodyY = Math.min(openY, closeY);
      const bodyH = Math.max(1, Math.abs(closeY - openY));
      ctx.fillRect(x - candleWidth * 0.35, bodyY, candleWidth * 0.7, bodyH);
    });

    // 4. Hybrid Reality Cone (10th - 90th percentile fan)
    if (realityCone && realityCone.p50 && realityCone.p50.length > 0) {
      const lastCandle = candles[candles.length - 1];
      const startConeX = (candles.length - 1) * candleWidth + candleWidth / 2;
      const basePrice = lastCandle.close;

      const p10Prices = realityCone.p10.map((pct) => basePrice * (1 + pct / 100));
      const p25Prices = realityCone.p25.map((pct) => basePrice * (1 + pct / 100));
      const p50Prices = realityCone.p50.map((pct) => basePrice * (1 + pct / 100));
      const p75Prices = realityCone.p75.map((pct) => basePrice * (1 + pct / 100));
      const p90Prices = realityCone.p90.map((pct) => basePrice * (1 + pct / 100));

      // 10th-90th fan
      ctx.fillStyle = "rgba(139, 92, 246, 0.12)";
      ctx.beginPath();
      ctx.moveTo(startConeX, priceToY(basePrice));
      p90Prices.forEach((p, i) => ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p)));
      for (let i = p10Prices.length - 1; i >= 0; i--) {
        ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p10Prices[i]));
      }
      ctx.closePath();
      ctx.fill();

      // 25th-75th fan
      ctx.fillStyle = "rgba(139, 92, 246, 0.22)";
      ctx.beginPath();
      ctx.moveTo(startConeX, priceToY(basePrice));
      p75Prices.forEach((p, i) => ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p)));
      for (let i = p25Prices.length - 1; i >= 0; i--) {
        ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p25Prices[i]));
      }
      ctx.closePath();
      ctx.fill();

      // 50th percentile (Median expected path)
      ctx.strokeStyle = "#A78BFA";
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.moveTo(startConeX, priceToY(basePrice));
      p50Prices.forEach((p, i) => ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p)));
      ctx.stroke();

      ctx.fillStyle = "#C4B5FD";
      ctx.font = "bold 10px monospace";
      ctx.fillText("Reality Cone (P50)", startConeX + p50Prices.length * candleWidth - 30, priceToY(p50Prices[p50Prices.length - 1]) - 8);
    }

    // 5. Ghost Analog Replay Path
    if (activeGhostTwin && activeGhostTwin.fwd_20_normalized_path) {
      const lastCandle = candles[candles.length - 1];
      const startConeX = (candles.length - 1) * candleWidth + candleWidth / 2;
      const basePrice = lastCandle.close;

      ctx.strokeStyle = "#F59E0B";
      ctx.lineWidth = 2.5;
      ctx.setLineDash([5, 3]);
      ctx.beginPath();
      ctx.moveTo(startConeX, priceToY(basePrice));

      activeGhostTwin.fwd_20_normalized_path.forEach((pct, i) => {
        const ghostP = basePrice * (1 + pct / 100);
        ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(ghostP));
      });
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = "#F59E0B";
      ctx.font = "bold 10px sans-serif";
      ctx.fillText(`Ghost Twin: ${activeGhostTwin.symbol} (${activeGhostTwin.match_pct}%)`, startConeX + 15, 60);
    }
  }, [candles, realityCone, activeGhostTwin, selectedRange, isDragging, dragStartIdx, dragCurrentIdx]);

  const currentCount = selectedRange[1] - selectedRange[0] + 1;

  return (
    <div ref={containerRef} className="relative w-full bg-background rounded-lg overflow-hidden border border-gray-800 flex flex-col">
      {/* Top Interactive Toolbar */}
      <div className="h-10 bg-surface/90 border-b border-gray-800 px-3 flex items-center justify-between text-xs select-none">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 font-bold text-gray-200">
            <MousePointer className="w-3.5 h-3.5 text-kronos" />
            Brush Tool:
          </span>
          <span className="text-kronos font-mono font-bold bg-kronos/15 px-2 py-0.5 rounded border border-kronos/30">
            {currentCount} Bars Selected
          </span>
          <span className="text-[11px] text-gray-400 hidden sm:inline">
            (Click & Drag across candles or click a quick preset)
          </span>
        </div>

        {/* Quick Window Presets */}
        <div className="flex items-center gap-1.5">
          <span className="text-gray-500 text-[11px]">Presets:</span>
          <button
            onClick={() => applyPreset(32)}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition ${
              currentCount === 32 ? "bg-kronos text-white" : "bg-surfaceElevated hover:bg-gray-700 text-gray-300"
            }`}
          >
            32b (Scalp)
          </button>
          <button
            onClick={() => applyPreset(64)}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition ${
              currentCount === 64 ? "bg-kronos text-white" : "bg-surfaceElevated hover:bg-gray-700 text-gray-300"
            }`}
          >
            64b (Swing)
          </button>
          <button
            onClick={() => applyPreset(128)}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition ${
              currentCount === 128 ? "bg-kronos text-white" : "bg-surfaceElevated hover:bg-gray-700 text-gray-300"
            }`}
          >
            128b (Regime)
          </button>
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="relative w-full h-[440px]">
        <canvas
          ref={canvasRef}
          className="w-full h-full cursor-crosshair select-none"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
        />

        {isDragging && dragStartIdx !== null && dragCurrentIdx !== null && (
          <div className="absolute top-3 left-3 bg-kronos text-white px-3 py-1 rounded shadow-lg text-xs font-bold flex items-center gap-1.5 animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            Selecting {Math.abs(dragCurrentIdx - dragStartIdx) + 1} Bars — Release to Scan
          </div>
        )}

        {isScanning && (
          <div className="absolute inset-0 bg-background/30 backdrop-blur-[1px] flex items-center justify-center">
            <div className="bg-surface/90 border border-kronos px-4 py-2 rounded-lg text-xs font-bold text-kronos flex items-center gap-2 shadow-2xl">
              <span className="w-2.5 h-2.5 rounded-full bg-kronos animate-ping"></span>
              Searching 50M+ Historical Windows in Qdrant...
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
