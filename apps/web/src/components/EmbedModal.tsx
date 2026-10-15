"use client";

import React, { useState } from "react";
import { Copy, Check, X, Code2 } from "lucide-react";

interface EmbedModalProps {
  isOpen: boolean;
  onClose: () => void;
  symbol: string;
  timeframe: string;
}

export const EmbedModal: React.FC<EmbedModalProps> = ({ isOpen, onClose, symbol, timeframe }) => {
  const [copied, setCopied] = useState(false);
  const [affiliateId, setAffiliateId] = useState("trader_vip");

  if (!isOpen) return null;

  const embedUrl = `https://xpredictor.com/embed/${symbol}/${timeframe}?ref=${affiliateId}`;
  const iframeCode = `<iframe src="${embedUrl}" width="100%" height="600" frameborder="0" allowfullscreen></iframe>`;

  const handleCopy = () => {
    navigator.clipboard.writeText(iframeCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-surface border border-gray-800 rounded-xl max-w-lg w-full p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 mb-3 text-kronos">
          <Code2 className="w-5 h-5" />
          <h3 className="font-bold text-lg text-white">Embed XPredictor Reality Cone</h3>
        </div>

        <p className="text-xs text-gray-400 mb-4">
          Embed this live interactive pattern scanner into your Substack newsletter, trading blog, or broker terminal. Includes 30% recurring creator affiliate commissions.
        </p>

        <div className="mb-4">
          <label className="text-xs text-gray-300 font-medium block mb-1">
            Your Affiliate / Partner ID:
          </label>
          <input
            type="text"
            value={affiliateId}
            onChange={(e) => setAffiliateId(e.target.value)}
            className="w-full bg-surfaceElevated border border-gray-700 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-kronos"
          />
        </div>

        <div className="mb-5">
          <label className="text-xs text-gray-300 font-medium block mb-1">
            Iframe Embed Code:
          </label>
          <div className="relative">
            <textarea
              readOnly
              rows={3}
              value={iframeCode}
              className="w-full bg-surfaceElevated border border-gray-700 rounded p-2 text-xs font-mono text-gray-300 focus:outline-none"
            />
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs rounded border border-gray-700 hover:bg-surfaceElevated text-gray-300"
          >
            Close
          </button>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded bg-kronos hover:bg-kronosMuted text-white transition shadow-lg shadow-kronos/20"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            {copied ? "Copied to Clipboard!" : "Copy Embed Code"}
          </button>
        </div>
      </div>
    </div>
  );
};
