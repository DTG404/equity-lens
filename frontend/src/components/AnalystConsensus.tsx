'use client';

import React, { useState, useEffect } from 'react';
import { fetchAnalystConsensus, AnalystRatings } from '@/lib/api';

interface Props {
  symbol: string;
}

export default function AnalystConsensus({ symbol }: Props) {
  const [data, setData] = useState<AnalystRatings | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchAnalystConsensus(symbol)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) {
    return (
      <div className="glass-panel p-4">
        <div className="animate-pulse h-4 bg-white/5 rounded w-1/3 mb-2" />
        <div className="animate-pulse h-8 bg-white/5 rounded w-1/2" />
      </div>
    );
  }

  if (!data || data.total_analysts === 0) {
    return (
      <div className="glass-panel p-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40">Analyst Consensus</h3>
        <p className="text-xs text-white/30 mt-2">No analyst data available.</p>
      </div>
    );
  }

  const total = data.total_analysts;
  const buyPct = total > 0 ? Math.round((data.ratings.buy / total) * 100) : 0;
  const holdPct = total > 0 ? Math.round((data.ratings.hold / total) * 100) : 0;
  const sellPct = total > 0 ? Math.round((data.ratings.sell / total) * 100) : 0;

  const consensusColors: Record<string, string> = {
    strong_buy: 'text-green-400',
    buy: 'text-green-400',
    hold: 'text-amber-400',
    sell: 'text-red-400',
  };

  const consensusLabels: Record<string, string> = {
    strong_buy: 'Strong Buy',
    buy: 'Buy',
    hold: 'Hold',
    sell: 'Sell',
  };

  return (
    <div className="glass-panel p-4">
      <button onClick={() => setExpanded(!expanded)} className="w-full text-left">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40">Analyst Consensus</h3>
          <span className="text-xs text-white/30">{expanded ? '▲' : '▼'}</span>
        </div>
        <div className="flex items-center gap-3 mt-2">
          <span className={`text-lg font-bold font-mono ${consensusColors[data.consensus] || 'text-white/60'}`}>
            {consensusLabels[data.consensus] || data.consensus}
          </span>
          <span className="text-xs text-white/30">({total} analysts)</span>
        </div>
        <div className="flex h-2 rounded-full overflow-hidden mt-2 bg-white/5">
          {buyPct > 0 && <div style={{ width: `${buyPct}%` }} className="bg-green-500/60" />}
          {holdPct > 0 && <div style={{ width: `${holdPct}%` }} className="bg-amber-500/60" />}
          {sellPct > 0 && <div style={{ width: `${sellPct}%` }} className="bg-red-500/60" />}
        </div>
        <div className="flex justify-between text-[0.55rem] text-white/30 mt-1">
          <span>Buy {buyPct}%</span>
          <span>Hold {holdPct}%</span>
          <span>Sell {sellPct}%</span>
        </div>
      </button>
    </div>
  );
}
