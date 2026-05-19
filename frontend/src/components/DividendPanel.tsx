'use client';

import React, { useState, useEffect } from 'react';
import { fetchDividends, DividendData } from '@/lib/api';

interface Props {
  symbol: string;
}

export default function DividendPanel({ symbol }: Props) {
  const [data, setData] = useState<DividendData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchDividends(symbol)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) {
    return (
      <div className="glass-panel p-4">
        <div className="animate-pulse h-4 bg-white/5 rounded w-1/3 mb-2" />
        <div className="animate-pulse h-3 bg-white/5 rounded w-1/2" />
      </div>
    );
  }

  if (!data || data.history.length === 0) {
    return (
      <div className="glass-panel p-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40">Dividends</h3>
        <p className="text-xs text-white/30 mt-2">No dividend data available.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-3">Dividends</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
        <div className="text-center">
          <div className="text-lg font-bold font-mono text-green-400">{data.dividend_yield}%</div>
          <div className="text-[0.55rem] uppercase text-white/30 mt-1">Yield</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold font-mono text-cyan-400">{data.payout_ratio}%</div>
          <div className="text-[0.55rem] uppercase text-white/30 mt-1">Payout</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold font-mono text-white/70">${data.dividend_per_share.toFixed(2)}</div>
          <div className="text-[0.55rem] uppercase text-white/30 mt-1">Per Share</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold font-mono text-amber-400">{data.history.length}</div>
          <div className="text-[0.55rem] uppercase text-white/30 mt-1">Payments</div>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-[0.6rem]">
          <thead>
            <tr className="text-white/30 border-b border-white/[0.04]">
              <th className="text-left py-1">Date</th>
              <th className="text-right py-1">Amount</th>
            </tr>
          </thead>
          <tbody>
            {data.history.slice(0, 10).map((h, i) => (
              <tr key={i} className="border-b border-white/[0.02]">
                <td className="py-1 text-white/50">{h.date}</td>
                <td className="text-right py-1 font-mono text-white/60">${h.amount.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
