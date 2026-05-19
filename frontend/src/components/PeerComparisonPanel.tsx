'use client';

import React, { useState, useEffect } from 'react';
import { fetchPeers, PeerData } from '@/lib/api';
import Link from 'next/link';

interface Props {
  symbol: string;
}

export default function PeerComparisonPanel({ symbol }: Props) {
  const [data, setData] = useState<PeerData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchPeers(symbol)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) {
    return (
      <div className="glass-panel p-4">
        <div className="animate-pulse h-4 bg-white/5 rounded w-1/3 mb-3" />
        <div className="animate-pulse h-3 bg-white/5 rounded w-full mb-2" />
        <div className="animate-pulse h-3 bg-white/5 rounded w-3/4" />
      </div>
    );
  }

  if (!data || data.peers.length === 0) {
    return null;
  }

  const metrics = [
    { key: 'market_cap', label: 'Market Cap', fmt: (v: number) => v >= 1e12 ? `$${(v/1e12).toFixed(1)}T` : v >= 1e9 ? `$${(v/1e9).toFixed(1)}B` : `$${(v/1e6).toFixed(0)}M` },
    { key: 'pe_ratio', label: 'P/E', fmt: (v: number) => v.toFixed(1) },
    { key: 'revenue_growth', label: 'Rev Growth', fmt: (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%` },
    { key: 'profit_margin', label: 'Margin', fmt: (v: number) => `${v.toFixed(1)}%` },
    { key: 'ytd_return', label: 'YTD', fmt: (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%` },
  ];

  const peersToShow = data.peers.slice(0, 5);
  const peerTickers = [symbol, ...peersToShow.map(p => p.symbol)];
  const compareUrl = `/compare?tickers=${peerTickers.join(',')}`;

  return (
    <div className="glass-panel p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40">
          vs Sector Peers
        </h3>
        <Link href={compareUrl} className="text-[0.6rem] text-cyan-400 hover:text-cyan-300 transition-colors">
          Compare All →
        </Link>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-white/30 text-[0.55rem] uppercase tracking-wider">
              <th className="text-left pr-2 py-1">Metric</th>
              <th className="text-right px-2 py-1 text-cyan-400">{symbol}</th>
              {peersToShow.map(p => (
                <th key={p.symbol} className="text-right px-2 py-1 text-white/40">{p.symbol}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metrics.map(({ key, label, fmt }) => (
              <tr key={key} className="border-t border-white/[0.03]">
                <td className="text-white/50 pr-2 py-1.5">{label}</td>
                <td className={`text-right px-2 py-1.5 font-mono font-semibold text-cyan-400`}>
                  {fmt(data.symbol_metrics[key] || 0)}
                </td>
                {peersToShow.map(p => {
                  const val = (p as any)[key] || 0;
                  return (
                    <td key={p.symbol} className="text-right px-2 py-1.5 font-mono text-white/50">
                      {fmt(val)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-white/[0.04]">
        {Object.entries(data.percentiles).map(([metric, pct]) => {
          const label = metrics.find(m => m.key === metric)?.label || metric;
          const color = pct >= 70 ? 'text-green-400' : pct >= 40 ? 'text-amber-400' : 'text-red-400';
          return (
            <span key={metric} className="text-[0.55rem] text-white/40">
              {label}: <span className={`font-semibold ${color}`}>Top {pct}%</span>
            </span>
          );
        })}
      </div>
    </div>
  );
}
