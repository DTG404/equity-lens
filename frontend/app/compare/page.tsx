'use client';

import React, { useState, useCallback, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';
import CompareTable from '@/components/CompareTable';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

interface CompareMetrics {
  price: number;
  change_pct: number;
  market_cap: number;
  pe_ratio: number;
  revenue_growth: number;
  profit_margin: number;
  rsi: number;
  sector: string;
}

interface CompareData {
  tickers: string[];
  metrics: Record<string, CompareMetrics>;
  best_values: Record<string, string>;
}

function CompareContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [input, setInput] = useState('');
  const [data, setData] = useState<CompareData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const tickersFromUrl = searchParams.get('tickers') ?? '';

  const fetchCompare = useCallback(async (tickers: string) => {
    if (!tickers) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/compare?tickers=${encodeURIComponent(tickers)}`);
      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail ?? `Error ${response.status}`);
      }
      const result = (await response.json()) as CompareData;
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load comparison');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (tickersFromUrl) {
      fetchCompare(tickersFromUrl);
    }
  }, [tickersFromUrl, fetchCompare]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleaned = input
      .split(/[,;\s]+/)
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean)
      .join(',');
    if (!cleaned) return;
    router.push(`/compare?tickers=${encodeURIComponent(cleaned)}`);
  };

  const handleRemove = (ticker: string) => {
    const current = tickersFromUrl
      .split(',')
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);
    const updated = current.filter((t) => t !== ticker).join(',');
    if (updated.split(',').length < 2) {
      router.push('/compare');
      setData(null);
      return;
    }
    router.push(`/compare?tickers=${encodeURIComponent(updated)}`);
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
              Ticker Comparison
            </h1>
          </div>

          {/* Input form */}
          <form onSubmit={handleSubmit} className="flex flex-wrap items-center gap-2 border-b border-white/[0.04] px-4 py-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter tickers (e.g., AAPL, MSFT, NVDA)"
              className="flex-1 rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-1.5 font-mono text-xs text-[#f0f6fc] placeholder-white/25 outline-none focus:border-cyan-400/30 min-w-[200px]"
            />
            <button
              type="submit"
              className="glass-badge-cyan rounded-lg px-4 py-1.5 text-xs font-semibold uppercase tracking-wider"
            >
              Compare
            </button>
          </form>

          {/* Loading */}
          {loading && (
            <div className="space-y-2 p-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-6 animate-pulse rounded-lg bg-white/[0.03]" />
              ))}
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div className="border-b border-white/[0.04] px-4 py-3 text-xs text-red-400">
              {error}
            </div>
          )}

          {/* Empty */}
          {!loading && !error && !data && !tickersFromUrl && (
            <div className="px-4 py-12 text-center text-xs text-white/25">
              Enter 2–5 ticker symbols to compare side by side
            </div>
          )}

          {/* Data */}
          {data && !loading && (
            <div>
              <div className="flex flex-wrap gap-1.5 border-b border-white/[0.03] px-4 py-2">
                {data.tickers.map((ticker) => (
                  <span
                    key={ticker}
                    className="inline-flex items-center gap-1 rounded-full border border-white/[0.08] px-2.5 py-0.5 font-mono text-[0.6rem] text-white/60"
                  >
                    {ticker}
                    <button
                      onClick={() => handleRemove(ticker)}
                      className="ml-0.5 text-white/30 hover:text-red-400 transition-colors"
                      aria-label={`Remove ${ticker}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <CompareTable data={data} />
            </div>
          )}
        </div>
      </main>

      <StatusBar />
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense
      fallback={
        <div className="relative flex min-h-screen flex-col">
          <div className="cosmic-bg" />
          <div className="cosmic-noise" />
          <NavBar />
          <main className="relative z-10 mx-3 my-3 flex-1">
            <div className="glass-panel mb-3 overflow-hidden p-4">
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-6 animate-pulse rounded-lg bg-white/[0.03]" />
                ))}
              </div>
            </div>
          </main>
          <StatusBar />
        </div>
      }
    >
      <CompareContent />
    </Suspense>
  );
}
