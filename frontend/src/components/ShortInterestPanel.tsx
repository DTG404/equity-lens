'use client';

import React, { useState, useEffect } from 'react';
import { fetchShortInterest, ShortInterestData } from '@/lib/api';

interface Props {
  symbol: string;
}

const SQUEEZE_COLORS: Record<string, string> = {
  potential: 'text-red-400',
  watch: 'text-amber-400',
  low: 'text-green-400',
};

const SQUEEZE_LABELS: Record<string, string> = {
  potential: 'Potential',
  watch: 'Watch',
  low: 'Low',
};

export default function ShortInterestPanel({ symbol }: Props) {
  const [data, setData] = useState<ShortInterestData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchShortInterest(symbol)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) {
    return (
      <div className="glass-panel p-4">
        <div className="animate-pulse h-4 bg-white/5 rounded w-1/3 mb-2" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="glass-panel p-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40">Short Interest</h3>
        <p className="text-xs text-white/30 mt-2">No data available.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40">Short Interest</h3>
        <span className={`text-[0.55rem] font-semibold uppercase ${SQUEEZE_COLORS[data.squeeze_signal] || 'text-white/40'}`}>
          Squeeze: {SQUEEZE_LABELS[data.squeeze_signal] || data.squeeze_signal}
        </span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="text-center">
          <div className={`text-lg font-bold font-mono ${data.short_percent_of_float > 10 ? 'text-red-400' : data.short_percent_of_float > 5 ? 'text-amber-400' : 'text-green-400'}`}>
            {data.short_percent_of_float}%
          </div>
          <div className="text-[0.55rem] uppercase text-white/30 mt-1">Short Float</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold font-mono text-cyan-400">{data.days_to_cover}</div>
          <div className="text-[0.55rem] uppercase text-white/30 mt-1">Days to Cover</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold font-mono text-white/70">{data.short_ratio.toFixed(1)}</div>
          <div className="text-[0.55rem] uppercase text-white/30 mt-1">Short Ratio</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold font-mono text-white/50">{(data.shares_short / 1000000).toFixed(1)}M</div>
          <div className="text-[0.55rem] uppercase text-white/30 mt-1">Shares Short</div>
        </div>
      </div>
    </div>
  );
}
