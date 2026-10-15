"use client";

import React from "react";
import { TrendingUp, TrendingDown, ShieldAlert, Award, Share2, Bell, Code } from "lucide-react";

interface ScoreCardProps {
  scoreData: {
    bullish_skew_pct: number;
    win_rate_20b: number;
    win_rate_10b: number;
    median_return_pct: number;
    median_max_dd_pct: number;
    optimal_rr: number;
    regime_breakdown: { crypto: number; fx_gold: number; equities: number };
    analog_count: number;
  };
  onShare: () => void;
  onAlert: () => void;
  onEmbed: () => void;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ scoreData, onShare, onAlert, onEmbed }) => {
  const isBullish = scoreData.bullish_skew_pct >= 50;

  return (
    <div className="flex flex-col h-full bg-surface border border-gray-800 rounded-lg p-4 space-y-4 text-sm">
      {/* Header Badge */}
      <div className="border-b border-gray-800 pb-3">
        <div className="text-xs uppercase tracking-wider text-gray-400 font-semibold mb-1">
          Historical Analog Score
        </div>
        <div className={`text-xl font-bold flex items-center gap-2 ${isBullish ? "text-bullish" : "text-bearish"}`}>
          {isBullish ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
          {scoreData.bullish_skew_pct}% {isBullish ? "Bullish Skew" : "Bearish Skew"}
        </div>
        <div className="text-xs text-gray-400 mt-1">
          Based on {scoreData.analog_count} nearest structural analogs (d_cos ≥ 0.82)
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="space-y-3 py-1">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Win Rate (+20 bars):</span>
          <span className="font-mono font-bold text-gray-100">{scoreData.win_rate_20b}%</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Win Rate (+10 bars):</span>
          <span className="font-mono text-gray-200">{scoreData.win_rate_10b}%</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Median Return (+20b):</span>
          <span className={`font-mono font-bold ${scoreData.median_return_pct >= 0 ? "text-bullish" : "text-bearish"}`}>
            {scoreData.median_return_pct >= 0 ? "+" : ""}{scoreData.median_return_pct}%
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Median Max Drawdown:</span>
          <span className="font-mono text-bearish">{scoreData.median_max_dd_pct}%</span>
        </div>
        <div className="flex justify-between items-center border-t border-gray-800/80 pt-2">
          <span className="text-gray-400 flex items-center gap-1">
            <Award className="w-3.5 h-3.5 text-kronos" /> Optimal R:R:
          </span>
          <span className="font-mono font-bold text-kronos">{scoreData.optimal_rr}x</span>
        </div>
      </div>

      {/* Regime Breakdown */}
      <div className="border-t border-gray-800 pt-3">
        <div className="text-xs uppercase tracking-wider text-gray-400 font-semibold mb-2">
          Regime Breakdown
        </div>
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="bg-surfaceElevated p-2 rounded border border-gray-800">
            <div className="text-gray-400">Crypto</div>
            <div className="font-mono font-bold text-indigo-400 mt-0.5">
              {scoreData.regime_breakdown.crypto}
            </div>
          </div>
          <div className="bg-surfaceElevated p-2 rounded border border-gray-800">
            <div className="text-gray-400">FX / Gold</div>
            <div className="font-mono font-bold text-amber-400 mt-0.5">
              {scoreData.regime_breakdown.fx_gold}
            </div>
          </div>
          <div className="bg-surfaceElevated p-2 rounded border border-gray-800">
            <div className="text-gray-400">Equities</div>
            <div className="font-mono font-bold text-emerald-400 mt-0.5">
              {scoreData.regime_breakdown.equities}
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="pt-2 space-y-2 mt-auto">
        <button
          onClick={onShare}
          className="w-full flex items-center justify-center gap-2 bg-kronos hover:bg-kronosMuted text-white py-2 px-3 rounded font-medium transition text-xs shadow-lg shadow-kronos/20"
        >
          <Share2 className="w-4 h-4" /> Share Reality Cone
        </button>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onAlert}
            className="flex items-center justify-center gap-1.5 bg-surfaceElevated hover:bg-gray-700 text-gray-200 py-2 px-2 rounded border border-gray-700 text-xs transition"
          >
            <Bell className="w-3.5 h-3.5 text-amber-400" /> Alert Setup
          </button>
          <button
            onClick={onEmbed}
            className="flex items-center justify-center gap-1.5 bg-surfaceElevated hover:bg-gray-700 text-gray-200 py-2 px-2 rounded border border-gray-700 text-xs transition"
          >
            <Code className="w-3.5 h-3.5 text-kronos" /> Embed Iframe
          </button>
        </div>
      </div>
    </div>
  );
};
