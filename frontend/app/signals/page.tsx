'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';
import { fetchSignalMetrics, fetchSignalOutcomes, type SignalMetrics, type SignalOutcome } from '@/lib/api';

export default function SignalsPage() {
  const [metrics, setMetrics] = useState<SignalMetrics | null>(null);
  const [outcomes, setOutcomes] = useState<SignalOutcome[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetchSignalMetrics(),
      fetchSignalOutcomes(),
    ])
      .then(([m, o]) => {
        setMetrics(m);
        setOutcomes(o);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />

      <main className="relative z-10 mx-3 my-3 flex-1">
        <div className="glass-panel mb-3 overflow-hidden">
          <div className="border-b border-white/[0.04] px-4 py-3">
            <h1 className="text-xs font-semibold uppercase tracking-wider text-white/40">
              Signal History
            </h1>
          </div>

          {loading ? (
            <div className="space-y-3 p-4">
              <div className="h-16 animate-pulse rounded-lg bg-white/[0.03]" />
              <div className="h-8 animate-pulse rounded-lg bg-white/[0.03]" />
            </div>
          ) : error ? (
            <div className="px-4 py-8 text-center text-xs text-red-400">{error}</div>
          ) : (
            <>
              {/* Metrics cards */}
              {metrics && (
                <div className="grid grid-cols-3 gap-3 border-b border-white/[0.04] p-4">
                  <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                    <div className="text-[0.6rem] uppercase tracking-wider text-white/30">Accuracy</div>
                    <div className="font-mono text-lg font-bold text-green-400">
                      {metrics.accuracy_pct.toFixed(1)}%
                    </div>
                  </div>
                  <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                    <div className="text-[0.6rem] uppercase tracking-wider text-white/30">Signals</div>
                    <div className="font-mono text-lg font-bold text-[#f0f6fc]">
                      {metrics.total_signals}
                    </div>
                  </div>
                  <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                    <div className="text-[0.6rem] uppercase tracking-wider text-white/30">Avg Return</div>
                    <div className={`font-mono text-lg font-bold ${metrics.avg_return >= 0 ? 'text-cyan-400' : 'text-red-400'}`}>
                      {metrics.avg_return >= 0 ? '+' : ''}{metrics.avg_return.toFixed(2)}%
                    </div>
                  </div>
                </div>
              )}

              {/* Outcomes table */}
              {outcomes.length === 0 ? (
                <div className="px-4 py-8 text-center text-xs text-white/25">
                  No signal outcomes yet. Signals are generated when you research stocks and tracked automatically by the scheduler.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-white/[0.03] text-[0.6rem] uppercase tracking-wider text-white/25">
                        <th className="px-3 py-2 text-left font-medium">Symbol</th>
                        <th className="px-3 py-2 text-left font-medium">Stance</th>
                        <th className="px-3 py-2 text-left font-medium">Window</th>
                        <th className="px-3 py-2 text-right font-medium">Return</th>
                        <th className="px-3 py-2 text-right font-medium">Result</th>
                      </tr>
                    </thead>
                    <tbody>
                      {outcomes.map((o) => (
                        <tr key={o.id} className="border-b border-white/[0.02] font-mono text-[0.65rem] last:border-0 hover:bg-white/[0.01]">
                          <td className="px-3 py-2">
                            <Link href={`/stocks/${o.symbol}`} className="font-semibold text-[#f0f6fc] no-underline hover:text-cyan-400">
                              {o.symbol}
                            </Link>
                          </td>
                          <td className="px-3 py-2 capitalize text-white/60">{o.stance}</td>
                          <td className="px-3 py-2 text-white/60">{o.window}</td>
                          <td className={`px-3 py-2 text-right font-semibold ${o.return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {o.return_pct >= 0 ? '+' : ''}{o.return_pct.toFixed(2)}%
                          </td>
                          <td className="px-3 py-2 text-right">
                            <span className={`inline-block rounded-full px-2 py-0.5 font-mono text-[0.55rem] font-semibold ${o.correct ? 'glass-badge-green' : 'glass-badge-red'}`}>
                              {o.correct ? 'Correct' : 'Incorrect'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <StatusBar />
    </div>
  );
}
