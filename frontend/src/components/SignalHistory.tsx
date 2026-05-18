'use client';

import React, { useEffect, useState } from 'react';
import {
  fetchSignalOutcomes,
  fetchSignalMetrics,
  type SignalOutcome,
  type SignalMetrics,
} from '@/lib/api';

interface SignalHistoryProps {
  symbol?: string;
}

export default function SignalHistory({ symbol }: SignalHistoryProps) {
  const [outcomes, setOutcomes] = useState<SignalOutcome[]>([]);
  const [metrics, setMetrics] = useState<SignalMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [outcomesData, metricsData] = await Promise.all([
          fetchSignalOutcomes(symbol),
          fetchSignalMetrics(),
        ]);
        if (!cancelled) {
          setOutcomes(outcomesData);
          setMetrics(metricsData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load signal history');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [symbol]);

  if (loading) {
    return (
      <div className="glass-panel p-4">
        <p className="text-xs text-white/30">Loading signal history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel p-4">
        <p className="text-xs text-red-400">{error}</p>
      </div>
    );
  }

  if (outcomes.length === 0) {
    return (
      <div className="glass-panel p-4">
        <p className="text-xs text-white/30">No signal outcomes available.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel overflow-hidden">
      {metrics && (
        <div className="flex gap-6 border-b border-white/[0.04] px-4 py-3">
          <div data-testid="accuracy-metric">
            <span className="text-[0.6rem] uppercase tracking-wider text-white/30">Accuracy</span>
            <div className="font-mono text-base font-bold text-[#f0f6fc]">
              {metrics.accuracy_pct.toFixed(2)}%
            </div>
          </div>
          <div data-testid="signals-count">
            <span className="text-[0.6rem] uppercase tracking-wider text-white/30">Signals</span>
            <div className="font-mono text-base font-bold text-[#f0f6fc]">
              {metrics.total_signals}
            </div>
          </div>
          <div data-testid="avg-return">
            <span className="text-[0.6rem] uppercase tracking-wider text-white/30">Avg Return</span>
            <div className={`font-mono text-base font-bold ${metrics.avg_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {metrics.avg_return >= 0 ? '+' : ''}
              {metrics.avg_return.toFixed(2)}%
            </div>
          </div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="border-b border-white/[0.03] text-[0.6rem] uppercase tracking-wider text-white/25">
              <th className="px-3 py-2 text-left font-medium">Symbol</th>
              <th className="px-3 py-2 text-left font-medium">Stance</th>
              <th className="px-3 py-2 text-left font-medium">Window</th>
              <th className="px-3 py-2 text-left font-medium">Return</th>
              <th className="px-3 py-2 text-left font-medium">Result</th>
            </tr>
          </thead>
          <tbody>
            {outcomes.map((outcome) => (
              <tr key={outcome.id} className="border-b border-white/[0.02] font-mono text-xs last:border-0">
                <td className="px-3 py-2 text-[#f0f6fc]">{outcome.symbol}</td>
                <td className="px-3 py-2 capitalize text-white/70">{outcome.stance}</td>
                <td className="px-3 py-2 text-white/70">{outcome.window}</td>
                <td className={`px-3 py-2 font-semibold ${outcome.return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {outcome.return_pct >= 0 ? '+' : ''}
                  {outcome.return_pct.toFixed(2)}%
                </td>
                <td className="px-3 py-2">
                  <span
                    className={`inline-block rounded-full px-2 py-0.5 font-mono text-[0.55rem] font-semibold ${
                      outcome.correct
                        ? 'glass-badge-green'
                        : 'glass-badge-red'
                    }`}
                  >
                    {outcome.correct ? 'Correct' : 'Incorrect'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
