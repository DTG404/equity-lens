'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';
import AllocationChart from '@/components/AllocationChart';
import PortfolioValueChart from '@/components/PortfolioValueChart';
import { fetchPortfolioPerformance, type PortfolioPerformance } from '@/lib/api';
import { fetchPortfolioAnalytics, type PortfolioAnalytics } from '@/lib/api';

export default function PortfolioPage() {
  const [data, setData] = useState<PortfolioPerformance | null>(null);
  const [analytics, setAnalytics] = useState<PortfolioAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);

  useEffect(() => {
    fetchPortfolioPerformance()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));

    fetchPortfolioAnalytics()
      .then(setAnalytics)
      .catch(console.error)
      .finally(() => setAnalyticsLoading(false));
  }, []);

  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />

      <main className="relative z-10 mx-3 my-3 flex-1">
        {/* Performance Panel */}
        <div className="glass-panel mb-3 overflow-hidden">
          <div className="border-b border-white/[0.04] px-4 py-3">
            <h1 className="text-xs font-semibold uppercase tracking-wider text-white/40">
              Portfolio Performance
            </h1>
          </div>

          {loading ? (
            <div className="space-y-3 p-4">
              <div className="h-16 animate-pulse rounded-lg bg-white/[0.03]" />
              <div className="h-8 animate-pulse rounded-lg bg-white/[0.03]" />
            </div>
          ) : data ? (
            <>
              {/* Summary cards */}
              <div className="grid grid-cols-2 gap-3 border-b border-white/[0.04] p-4 sm:grid-cols-4">
                <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                  <div className="text-[0.6rem] uppercase tracking-wider text-white/30">Total Value</div>
                  <div className="font-mono text-lg font-bold text-[#f0f6fc]">${data.total_value.toLocaleString()}</div>
                </div>
                <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                  <div className="text-[0.6rem] uppercase tracking-wider text-white/30">Cost Basis</div>
                  <div className="font-mono text-lg font-bold text-[#f0f6fc]">${data.total_cost.toLocaleString()}</div>
                </div>
                <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                  <div className="text-[0.6rem] uppercase tracking-wider text-white/30">P&amp;L</div>
                  <div className={`font-mono text-lg font-bold ${data.total_pl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {data.total_pl >= 0 ? '+' : ''}${data.total_pl.toLocaleString()}
                  </div>
                </div>
                <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                  <div className="text-[0.6rem] uppercase tracking-wider text-white/30">Return</div>
                  <div className={`font-mono text-lg font-bold ${data.total_pl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {data.total_pl_pct >= 0 ? '+' : ''}{data.total_pl_pct.toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* Positions table */}
              {data.positions.length === 0 ? (
                <div className="px-4 py-8 text-center text-xs text-white/25">
                  No positions. Add holdings from the Dashboard.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-white/[0.03] text-[0.6rem] uppercase tracking-wider text-white/25">
                        <th className="px-3 py-2 text-left font-medium">Symbol</th>
                        <th className="px-3 py-2 text-right font-medium">Qty</th>
                        <th className="px-3 py-2 text-right font-medium">Avg Cost</th>
                        <th className="px-3 py-2 text-right font-medium">Current</th>
                        <th className="px-3 py-2 text-right font-medium">Market Value</th>
                        <th className="px-3 py-2 text-right font-medium">P&amp;L</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.positions.map((pos) => (
                        <tr key={pos.symbol} className="border-b border-white/[0.02] font-mono text-[0.65rem] last:border-0 hover:bg-white/[0.01]">
                          <td className="px-3 py-2">
                            <Link href={`/stocks/${pos.symbol}`} className="font-semibold text-[#f0f6fc] no-underline hover:text-cyan-400">
                              {pos.symbol}
                            </Link>
                          </td>
                          <td className="px-3 py-2 text-right text-[#f0f6fc]">{pos.quantity}</td>
                          <td className="px-3 py-2 text-right text-white/60">${pos.avg_cost.toFixed(2)}</td>
                          <td className="px-3 py-2 text-right text-[#f0f6fc]">${pos.current_price.toFixed(2)}</td>
                          <td className="px-3 py-2 text-right text-[#f0f6fc]">${pos.market_value.toLocaleString()}</td>
                          <td className={`px-3 py-2 text-right font-semibold ${pos.pl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {pos.pl >= 0 ? '+' : ''}${pos.pl.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <div className="px-4 py-8 text-center text-xs text-red-400">Failed to load portfolio data</div>
          )}
        </div>

        {/* Analytics Grid */}
        {analyticsLoading ? (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="h-[320px] animate-pulse rounded-2xl bg-white/[0.03]" />
            <div className="h-[320px] animate-pulse rounded-2xl bg-white/[0.03]" />
          </div>
        ) : analytics ? (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <AllocationChart
              sectors={analytics.allocation.by_sector}
              totalValue={analytics.allocation.total_value}
            />
            <PortfolioValueChart data={analytics.value_history} />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="glass-panel flex h-[320px] items-center justify-center">
              <span className="text-sm text-red-400">Failed to load analytics</span>
            </div>
            <div className="glass-panel flex h-[320px] items-center justify-center">
              <span className="text-sm text-red-400">Failed to load analytics</span>
            </div>
          </div>
        )}
      </main>

      <StatusBar />
    </div>
  );
}
