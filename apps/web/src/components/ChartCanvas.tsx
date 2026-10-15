"use client";

import React, { useEffect, useRef, useState } from "react";
import { HistoricalTwinItem } from "./AnalogCarousel";

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
}

export const ChartCanvas: React.FC<ChartCanvasProps> = ({
  candles,
  realityCone,
  activeGhostTwin,
  selectedRange,
  onRangeChange,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartIdx, setDragStartIdx] = useState<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Resize canvas to container
    const width = canvas.parentElement?.clientWidth || 800;
    const height = 480;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // Clear background
    ctx.fillStyle = "#090D16";
    ctx.fillRect(0, 0, width, height);

    if (candles.length === 0) return;

    // Determine price range
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    candles.forEach((c) => {
      minPrice = Math.min(minPrice, c.low);
      maxPrice = Math.max(maxPrice, c.high);
    });

    // Padding for reality cone expansion
    const pricePadding = (maxPrice - minPrice) * 0.15;
    minPrice -= pricePadding;
    maxPrice += pricePadding;

    const candleWidth = Math.max(3, (width - 120) / (candles.length + 22));
    const priceToY = (p: number) => height - 40 - ((p - minPrice) / (maxPrice - minPrice)) * (height - 80);

    // 1. Draw Grid lines
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

    // 2. Draw Brush Selection Area (translucent violet)
    const [startIdx, endIdx] = selectedRange;
    if (startIdx >= 0 && endIdx < candles.length) {
      const brushX = startIdx * candleWidth;
      const brushW = (endIdx - startIdx + 1) * candleWidth;
      ctx.fillStyle = "rgba(139, 92, 246, 0.15)";
      ctx.fillRect(brushX, 20, brushW, height - 60);

      ctx.strokeStyle = "#8B5CF6";
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.strokeRect(brushX, 20, brushW, height - 60);
      ctx.setLineDash([]);

      // Label
      ctx.fillStyle = "#8B5CF6";
      ctx.font = "bold 11px sans-serif";
      ctx.fillText(`Brush: ${endIdx - startIdx + 1} Bars`, brushX + 8, 36);
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

    // 4. Draw Hybrid Reality Cone (Quantile Fan)
    if (realityCone && realityCone.p50 && realityCone.p50.length > 0) {
      const lastCandle = candles[candles.length - 1];
      const startConeX = (candles.length - 1) * candleWidth + candleWidth / 2;
      const basePrice = lastCandle.close;

      const p10Prices = realityCone.p10.map((pct) => basePrice * (1 + pct / 100));
      const p25Prices = realityCone.p25.map((pct) => basePrice * (1 + pct / 100));
      const p50Prices = realityCone.p50.map((pct) => basePrice * (1 + pct / 100));
      const p75Prices = realityCone.p75.map((pct) => basePrice * (1 + pct / 100));
      const p90Prices = realityCone.p90.map((pct) => basePrice * (1 + pct / 100));

      // Shaded 10th-90th fan
      ctx.fillStyle = "rgba(139, 92, 246, 0.12)";
      ctx.beginPath();
      ctx.moveTo(startConeX, priceToY(basePrice));
      p90Prices.forEach((p, i) => ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p)));
      for (let i = p10Prices.length - 1; i >= 0; i--) {
        ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p10Prices[i]));
      }
      ctx.closePath();
      ctx.fill();

      // Shaded 25th-75th fan
      ctx.fillStyle = "rgba(139, 92, 246, 0.22)";
      ctx.beginPath();
      ctx.moveTo(startConeX, priceToY(basePrice));
      p75Prices.forEach((p, i) => ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p)));
      for (let i = p25Prices.length - 1; i >= 0; i--) {
        ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p25Prices[i]));
      }
      ctx.closePath();
      ctx.fill();

      // Median Line (50th percentile)
      ctx.strokeStyle = "#A78BFA";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(startConeX, priceToY(basePrice));
      p50Prices.forEach((p, i) => ctx.lineTo(startConeX + (i + 1) * candleWidth, priceToY(p)));
      ctx.stroke();

      // Reality Cone Tag
      ctx.fillStyle = "#C4B5FD";
      ctx.font = "bold 10px monospace";
      ctx.fillText("Reality Cone (P50)", startConeX + p50Prices.length * candleWidth - 30, priceToY(p50Prices[p50Prices.length - 1]) - 8);
    }

    // 5. Draw Ghost Analog Replay Path (if selected)
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
  }, [candles, realityCone, activeGhostTwin, selectedRange]);

  // Handle Drag Selection
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const width = canvas.clientWidth;
    const candleWidth = Math.max(3, (width - 120) / (candles.length + 22));
    const idx = Math.min(candles.length - 1, Math.max(0, Math.floor(x / candleWidth)));

    setIsDragging(true);
    setDragStartIdx(idx);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging || dragStartIdx === null) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const width = canvas.clientWidth;
    const candleWidth = Math.max(3, (width - 120) / (candles.length + 22));
    const currentIdx = Math.min(candles.length - 1, Math.max(0, Math.floor(x / candleWidth)));

    const start = Math.min(dragStartIdx, currentIdx);
    const end = Math.max(dragStartIdx, currentIdx);

    // Limit brush window to [32, 128]
    if (end - start + 1 >= 32 && end - start + 1 <= 128) {
      onRangeChange(start, end);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setDragStartIdx(null);
  };

  return (
    <div ref={containerRef} className="relative w-full h-[480px] bg-background rounded-lg overflow-hidden border border-gray-800">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-crosshair"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      />
      <div className="absolute top-2 left-3 flex items-center gap-2 bg-surface/80 backdrop-blur px-2.5 py-1 rounded border border-gray-800 text-[11px] text-gray-400">
        <span className="inline-block w-2 h-2 rounded-full bg-bullish animate-pulse"></span>
        <span>Hold & Drag on candles to Brush (32 - 128 bars)</span>
      </div>
    </div>
  );
};
