'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';
import { fetchScreener, type ScreenerResult } from '@/lib/api';

const SECTORS = [
  '', 'Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical',
  'Communication Services', 'Industrials', 'Consumer Defensive', 'Energy',
];

export default function ScreenerPage() {
  const [results, setResults] = useState<ScreenerResult[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [sector, setSector] = useState('');
  const [rsiMin, setRsiMin] = useState('');
  const [rsiMax, setRsiMax] = useState('');
  const [sortBy, setSortBy] = useState('symbol');
  const [sortDir, setSortDir] = useState('asc');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { sortBy, sortDir, limit: 50 };
      if (priceMin) params.priceMin = parseFloat(priceMin);
      if (priceMax) params.priceMax = parseFloat(priceMax);
      if (sector) params.sector = sector;
      if (rsiMin) params.rsiMin = parseFloat(rsiMin);
      if (rsiMax) params.rsiMax = parseFloat(rsiMax);

      const data = await fetchScreener(params as any);
      setResults(data.results);
      setTotal(data.total);
    } catch (err) {
      console.error('Screener error:', err);
    } finally {
      setLoading(false);
    }
  }, [priceMin, priceMax, sector, rsiMin, rsiMax, sortBy, sortDir]);

  useEffect(() => { load(); }, [load]);

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortDir('desc');
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />

      <main className="relative z-10 mx-3 my-3 flex-1">
        <div className="glass-panel mb-3 overflow-hidden">
          <div className="border-b border-white/[0.04] px-4 py-3">
            <h1 className="text-xs font-semibold uppercase tracking-wider text-white/40">
              Stock Screener
            </h1>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-2 border-b border-white/[0.04] px-4 py-3">
            <input
              type="number" placeholder="Min Price" value={priceMin}
              onChange={(e) => setPriceMin(e.target.value)}
              className="w-24 rounded-lg border border-white/[0.06] bg-white/[0.03] px-2 py-1.5 font-mono text-xs text-[#f0f6fc] placeholder-white/25 outline-none focus:border-cyan-400/30"
            />
            <input
              type="number" placeholder="Max Price" value={priceMax}
              onChange={(e) => setPriceMax(e.target.value)}
              className="w-24 rounded-lg border border-white/[0.06] bg-white/[0.03] px-2 py-1.5 font-mono text-xs text-[#f0f6fc] placeholder-white/25 outline-none focus:border-cyan-400/30"
            />
            <select
              value={sector} onChange={(e) => setSector(e.target.value)}
              className="rounded-lg border border-white/[0.06] bg-white/[0.03] px-2 py-1.5 text-xs text-white/60 outline-none focus:border-cyan-400/30"
            >
              {SECTORS.map((s) => (
                <option key={s} value={s} className="bg-[#0a0a1a]">{s || 'All Sectors'}</option>
              ))}
            </select>
            <input
              type="number" placeholder="RSI Min" value={rsiMin}
              onChange={(e) => setRsiMin(e.target.value)}
              className="w-20 rounded-lg border border-white/[0.06] bg-white/[0.03] px-2 py-1.5 font-mono text-xs text-[#f0f6fc] placeholder-white/25 outline-none focus:border-cyan-400/30"
            />
            <input
              type="number" placeholder="RSI Max" value={rsiMax}
              onChange={(e) => setRsiMax(e.target.value)}
              className="w-20 rounded-lg border border-white/[0.06] bg-white/[0.03] px-2 py-1.5 font-mono text-xs text-[#f0f6fc] placeholder-white/25 outline-none focus:border-cyan-400/30"
            />
            <button
              onClick={load}
              className="glass-badge-cyan rounded-lg px-4 py-1.5 text-xs font-semibold uppercase tracking-wider"
            >
              Filter
            </button>
          </div>

          {/* Results */}
          {loading ? (
            <div className="space-y-2 p-4">
              {[1,2,3,4,5].map((i) => (
                <div key={i} className="h-8 animate-pulse rounded-lg bg-white/[0.03]" />
              ))}
            </div>
          ) : (
            <>
              <div className="border-b border-white/[0.03] px-4 py-1 text-[0.55rem] text-white/20">
                {total} results
              </div>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-white/[0.03] text-[0.6rem] uppercase tracking-wider text-white/25">
                      {[
                        { key: 'symbol', label: 'Symbol' },
                        { key: 'price', label: 'Price' },
                        { key: 'change_percent', label: 'Change' },
                        { key: 'volume', label: 'Volume' },
                        { key: 'rsi', label: 'RSI' },
                        { key: 'pe_ratio', label: 'P/E' },
                        { key: 'market_cap', label: 'Mkt Cap' },
                      ].map((col) => (
                        <th
                          key={col.key}
                          onClick={() => handleSort(col.key)}
                          className="cursor-pointer px-3 py-2 text-left font-medium transition-colors hover:text-white/60"
                        >
                          {col.label} {sortBy === col.key ? (sortDir === 'asc' ? '▲' : '▼') : ''}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((r) => (
                      <tr key={r.symbol} className="border-b border-white/[0.02] font-mono text-[0.65rem] last:border-0 hover:bg-white/[0.01]">
                        <td className="px-3 py-2">
                          <Link href={`/stocks/${r.symbol}`} className="font-semibold text-[#f0f6fc] no-underline hover:text-cyan-400">
                            {r.symbol}
                          </Link>
                        </td>
                        <td className="px-3 py-2 text-[#f0f6fc]">${r.price.toFixed(2)}</td>
                        <td className={`px-3 py-2 ${r.change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {r.change_percent >= 0 ? '+' : ''}{r.change_percent.toFixed(2)}%
                        </td>
                        <td className="px-3 py-2 text-white/60">{r.volume.toLocaleString()}</td>
                        <td className={`px-3 py-2 ${r.rsi !== null ? (r.rsi > 70 ? 'text-red-400' : r.rsi < 30 ? 'text-green-400' : 'text-[#f0f6fc]') : 'text-white/30'}`}>
                          {r.rsi?.toFixed(1) ?? '—'}
                        </td>
                        <td className="px-3 py-2 text-white/60">{r.pe_ratio?.toFixed(1) ?? '—'}</td>
                        <td className="px-3 py-2 text-white/60">
                          {r.market_cap ? `$${(r.market_cap / 1e9).toFixed(1)}B` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {results.length === 0 && (
                <div className="px-4 py-8 text-center text-xs text-white/25">No results match your filters</div>
              )}
            </>
          )}
        </div>
      </main>

      <StatusBar />
    </div>
  );
}
