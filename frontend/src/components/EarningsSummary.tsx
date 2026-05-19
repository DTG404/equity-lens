'use client';

import React, { useState, useEffect } from 'react';
import { fetchEarningsSummary, EarningsSummary as ES } from '@/lib/api';

interface Props {
  symbol: string;
}

export default function EarningsSummaryCard({ symbol }: Props) {
  const [data, setData] = useState<ES | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchEarningsSummary(symbol)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) {
    return (
      <div className="glass-panel p-4">
        <div className="animate-pulse h-4 bg-white/5 rounded w-1/3 mb-2" />
        <div className="animate-pulse h-3 bg-white/5 rounded w-full" />
      </div>
    );
  }

  if (!data?.summary) {
    return (
      <div className="glass-panel p-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40">Earnings Summary</h3>
        <p className="text-xs text-white/30 mt-2">No earnings data available.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-3">Earnings Summary</h3>
      {data.quarterly_trend && (
        <div className="grid grid-cols-3 gap-3 mb-3">
          <div className="text-center">
            <div className="text-lg font-bold font-mono text-green-400">{data.quarterly_trend.beat_rate}%</div>
            <div className="text-[0.55rem] uppercase text-white/30 mt-1">Beat Rate</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold font-mono text-cyan-400">+{data.quarterly_trend.avg_surprise_pct}%</div>
            <div className="text-[0.55rem] uppercase text-white/30 mt-1">Avg Surprise</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold font-mono text-white/70">{data.quarterly_trend.beat_count}/{data.quarterly_trend.total_quarters}</div>
            <div className="text-[0.55rem] uppercase text-white/30 mt-1">Beat/Miss</div>
          </div>
        </div>
      )}
      <p className="text-xs text-white/60 leading-relaxed">{data.summary}</p>
    </div>
  );
}
