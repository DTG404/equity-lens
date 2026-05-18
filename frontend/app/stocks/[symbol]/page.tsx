'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { fetchResearch, type ResearchData } from '@/lib/api';
import PriceChart from '@/components/PriceChart';
import FactorScoreCard from '@/components/FactorScoreCard';
import ScenarioCard from '@/components/ScenarioCard';
import SignalHistory from '@/components/SignalHistory';
import { FundamentalsPanel, TechnicalsPanel } from '@/components/ResearchPanels';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';

interface ResearchPageProps {
  params: Promise<{ symbol: string }>;
}

function formatRelativeTime(dateString: string | null): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  if (diffDay > 0) return `${diffDay}d ago`;
  if (diffHour > 0) return `${diffHour}h ago`;
  if (diffMin > 0) return `${diffMin}m ago`;
  return 'just now';
}

export default function ResearchPage({ params }: ResearchPageProps) {
  const [data, setData] = useState<ResearchData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [symbol, setSymbol] = useState<string>('');
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('3M');

  const now = new Date();

  const filterByPeriod = (history: ResearchData['price_history'], period: string) => {
    if (period === 'ALL') return history;
    const days = { '1D': 1, '1W': 7, '1M': 30, '3M': 90, '1Y': 365 }[period] ?? 90;
    const cutoff = new Date(now.getTime() - days * 86400000);
    return history.filter((h) => new Date(h.date).getTime() >= cutoff.getTime());
  };

  const periods = ['1D', '1W', '1M', '3M', '1Y', 'ALL'];

  const loadResearch = useCallback(async (forceRegenerate?: boolean) => {
    try {
      const resolved = await params;
      const sym = resolved.symbol.toUpperCase();
      setSymbol(sym);
      const research = await fetchResearch(sym, forceRegenerate);
      setData(research);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load research');
    }
  }, [params]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const resolved = await params;
        const sym = resolved.symbol.toUpperCase();
        setSymbol(sym);
        const research = await fetchResearch(sym, true);
        if (!cancelled) setData(research);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load research');
      }
    }
    load();
    return () => { cancelled = true; };
  }, [params]);

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    await loadResearch(true);
    setIsRegenerating(false);
  };

  const changeColor =
    !data?.quote || data.quote.change_percent === 0
      ? 'text-white/40'
      : data.quote.change_percent > 0
        ? 'text-green-400'
        : 'text-red-400';

  const changeSign =
    !data?.quote || data.quote.change_percent === 0
      ? ''
      : data.quote.change_percent > 0
        ? '+'
        : '';

  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />

      <main className="relative z-10 mx-3 my-3 flex-1">
        {/* Breadcrumb */}
        <div className="mb-3">
          <Link
            href="/"
            className="inline-flex items-center gap-1 text-xs text-white/40 no-underline transition-colors hover:text-cyan-400"
          >
            <span>←</span>
            <span>Dashboard</span>
          </Link>
          <span className="mx-2 text-xs text-white/20">/</span>
          <span className="text-xs text-white/60">{symbol}</span>
        </div>

        {error && (
          <div className="glass-panel mb-3 px-4 py-3">
            <p className="text-xs text-red-400">{error}</p>
          </div>
        )}

        {data && (
          <>
            {/* Quote header */}
            <div className="glass-panel mb-3 flex items-center gap-4 px-4 py-3">
              <div>
                <h1 className="font-mono text-2xl font-bold text-[#f0f6fc]">{symbol}</h1>
                <div className="text-xs text-white/40">Apple Inc.</div>
              </div>
              {data.quote && (
                <div className="flex items-baseline gap-2">
                  <span className="font-mono text-xl font-bold text-[#f0f6fc]">
                    ${data.quote.price.toFixed(2)}
                  </span>
                  <span className={`font-mono text-sm font-semibold ${changeColor}`}>
                    {changeSign}
                    {data.quote.change_percent.toFixed(2)}%
                  </span>
                </div>
              )}
              <div className="ml-auto flex gap-2">
                <span className="glass-badge-cyan rounded-lg px-3 py-1.5 text-[0.6rem] font-semibold uppercase tracking-wider">
                  AI Signal
                </span>
                <button
                  onClick={handleRegenerate}
                  disabled={isRegenerating}
                  className="glass-badge-cyan rounded-lg px-3 py-1.5 text-[0.6rem] font-semibold uppercase tracking-wider transition-opacity hover:opacity-80 disabled:opacity-50"
                >
                  {isRegenerating ? 'Regenerating...' : 'Regenerate'}
                </button>
              </div>
            </div>

            {/* Main grid: Chart + Factors */}
            <div className="mb-3 grid grid-cols-1 gap-3 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <div className="glass-panel p-0">
                  <div className="flex items-center justify-between border-b border-white/[0.04] px-4 py-3">
                    <h2 className="text-xs font-semibold uppercase tracking-wider text-white/40">
                      Price Chart
                    </h2>
                    <div className="flex gap-1">
                      {periods.map((p) => (
                        <button
                          key={p}
                          onClick={() => setSelectedPeriod(p)}
                          className={`rounded-md px-1.5 py-0.5 font-mono text-[0.55rem] transition-colors ${
                            selectedPeriod === p
                              ? 'bg-cyan-400/10 text-cyan-400'
                              : 'text-white/30 hover:text-white/60'
                          }`}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="px-2 py-2">
                    <PriceChart
                      data={filterByPeriod(data.price_history, selectedPeriod).map((h) => ({
                        date: h.date,
                        open: h.open,
                        high: h.high,
                        low: h.low,
                        close: h.close,
                        volume: h.volume,
                      }))}
                    />
                  </div>
                </div>
              </div>

              <div>
                <FactorScoreCard scores={data.scores} />
              </div>
            </div>

            {/* Fundamentals + Technicals */}
            <div className="mb-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
              <FundamentalsPanel symbol={symbol} />
              <TechnicalsPanel symbol={symbol} />
            </div>

            {/* Thesis + Scenarios */}
            <div className="mb-3 grid grid-cols-1 gap-3 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <div className="glass-panel p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <span className="text-cyan-400">◆</span>
                    <h2 className="text-xs font-semibold uppercase tracking-wider text-white/40">
                      AI Thesis
                    </h2>
                  </div>
                  <p className="text-xs leading-relaxed text-white/60">{data.thesis}</p>
                  <div className="mt-3 flex items-center gap-2 border-t border-white/[0.04] pt-2">
                    <span className="font-mono text-[0.55rem] text-white/20">
                      Model: {data.scenarios.model}
                    </span>
                    <span className="font-mono text-[0.55rem] text-white/20">
                      Analysis #{data.analysis_id}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <div className="glass-panel p-4">
                  <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-white/40">
                    Risks
                  </div>
                  <p className="text-xs leading-relaxed text-white/50">{data.risks}</p>
                </div>
              </div>
            </div>

            {/* Scenarios */}
            <div className="mb-3">
              <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-white/40">
                Scenarios
              </div>
              <ScenarioCard
                bullCase={data.scenarios.bull_case}
                baseCase={data.scenarios.base_case}
                bearCase={data.scenarios.bear_case}
              />
            </div>

            {/* News */}
            <div className="mb-3">
              <div className="glass-panel">
                <div className="flex items-center justify-between border-b border-white/[0.04] px-4 py-3">
                  <h2 className="text-xs font-semibold uppercase tracking-wider text-white/40">
                    News
                  </h2>
                  {data.news.length > 0 && (
                    <span className="font-mono text-[0.55rem] text-white/20">
                      {data.news.length} articles
                    </span>
                  )}
                </div>
                <div className="px-4 py-2">
                  {data.news.length === 0 ? (
                    <p className="py-3 text-center text-xs text-white/25">No recent news.</p>
                  ) : (
                    data.news.map((article) => (
                      <div
                        key={article.id}
                        className="border-b border-white/[0.03] py-2.5 last:border-0"
                      >
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mb-1 block text-sm font-semibold text-[#f0f6fc] no-underline transition-colors hover:text-cyan-400"
                        >
                          {article.title}
                        </a>
                        <div className="flex justify-between text-xs">
                          <span className="text-white/40">{article.source}</span>
                          <span className="text-white/25">
                            {formatRelativeTime(article.published_at)}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Signal History */}
            <div className="mb-3">
              <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-white/40">
                Signal History
              </div>
              <SignalHistory symbol={symbol} />
            </div>
          </>
        )}
      </main>

      <StatusBar />
    </div>
  );
}
