"use client";

import React, { use } from "react";
import { PatternTerminal } from "@/components/PatternTerminal";

interface EmbedPageProps {
  params: Promise<{
    symbol: string;
    timeframe: string;
  }>;
}

export default function EmbedPage({ params }: EmbedPageProps) {
  const resolvedParams = use(params);

  return (
    <div className="w-full h-full bg-background min-h-screen">
      <div className="px-3 py-1 bg-surfaceElevated border-b border-gray-800 flex justify-between items-center text-[11px] text-gray-400">
        <span>Powered by <strong className="text-kronos">XPredictor</strong> ({resolvedParams.symbol.toUpperCase()} {resolvedParams.timeframe})</span>
        <a
          href="https://xpredictor.com"
          target="_blank"
          rel="noreferrer"
          className="text-kronos hover:underline"
        >
          Open Full Terminal →
        </a>
      </div>
      <PatternTerminal />
    </div>
  );
}
