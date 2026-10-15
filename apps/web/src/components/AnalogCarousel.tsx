"use client";

import React from "react";
import { Sparkles, Eye } from "lucide-react";

export interface HistoricalTwinItem {
  symbol: string;
  asset_class: string;
  timeframe: string;
  date_formatted: string;
  start_ts: number;
  end_ts: number;
  match_pct: number;
  fwd_20_ret_pct: number;
  fwd_20_max_dd_pct: number;
  fwd_20_normalized_path: number[];
}

interface AnalogCarouselProps {
  twins: HistoricalTwinItem[];
  activeTwin: HistoricalTwinItem | null;
  onSelectTwin: (twin: HistoricalTwinItem) => void;
}

export const AnalogCarousel: React.FC<AnalogCarouselProps> = ({ twins, activeTwin, onSelectTwin }) => {
  return (
    <div className="w-full bg-surface border border-gray-800 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs uppercase tracking-wider text-gray-400 font-semibold flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-kronos" /> Top Historical Twins (Click for Ghost Overlay)
        </div>
        <div className="text-xs text-gray-500">
          Replaying structural analog price paths directly on canvas
        </div>
      </div>

      <div className="flex gap-3 overflow-x-auto pb-1">
        {twins.map((twin, idx) => {
          const isSelected = activeTwin?.date_formatted === twin.date_formatted && activeTwin?.symbol === twin.symbol;
          const isPositive = twin.fwd_20_ret_pct >= 0;

          return (
            <div
              key={`${twin.symbol}-${idx}`}
              onClick={() => onSelectTwin(twin)}
              className={`flex-shrink-0 cursor-pointer p-2.5 rounded-lg border transition-all duration-150 min-w-[210px] ${
                isSelected
                  ? "bg-kronos/10 border-kronos shadow-md shadow-kronos/10"
                  : "bg-surfaceElevated border-gray-800 hover:border-gray-700"
              }`}
            >
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-gray-200">
                  #{idx + 1}: {twin.symbol}
                </span>
                <span className="text-gray-400 text-[11px]">{twin.date_formatted}</span>
              </div>

              <div className="mt-2 flex justify-between items-end">
                <div>
                  <div className="text-[11px] text-gray-400">Match</div>
                  <div className="font-mono text-xs font-bold text-kronos">{twin.match_pct}%</div>
                </div>
                <div className="text-right">
                  <div className="text-[11px] text-gray-400">20b Return</div>
                  <div className={`font-mono text-xs font-bold ${isPositive ? "text-bullish" : "text-bearish"}`}>
                    {isPositive ? "+" : ""}{twin.fwd_20_ret_pct}%
                  </div>
                </div>
              </div>

              {isSelected && (
                <div className="mt-2 pt-1.5 border-t border-kronos/30 flex items-center justify-center gap-1 text-[11px] text-ghostGold">
                  <Eye className="w-3 h-3" /> Ghost Replay Active
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
