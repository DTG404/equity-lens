'use client';

import React, { useEffect, useState } from 'react';
import { fetchSignalOutcomes, fetchSignalMetrics, type SignalOutcome, type SignalMetrics } from '@/lib/api';

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
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [symbol]);

  if (loading) {
    return (
      <div
        style={{
          background: 'var(--bg-card)',
          borderRadius: 8,
          padding: 16,
          border: '1px solid var(--border)',
        }}
      >
        <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Loading signal history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          background: 'var(--bg-card)',
          borderRadius: 8,
          padding: 16,
          border: '1px solid var(--border)',
        }}
      >
        <p style={{ fontSize: 13, color: 'var(--accent-red)' }}>{error}</p>
      </div>
    );
  }

  if (outcomes.length === 0) {
    return (
      <div
        style={{
          background: 'var(--bg-card)',
          borderRadius: 8,
          padding: 16,
          border: '1px solid var(--border)',
        }}
      >
        <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>No signal outcomes available.</p>
      </div>
    );
  }

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        borderRadius: 8,
        padding: 16,
        border: '1px solid var(--border)',
      }}
    >
      {metrics && (
        <div
          style={{
            display: 'flex',
            gap: 24,
            marginBottom: 16,
            flexWrap: 'wrap',
          }}
        >
          <div data-testid="accuracy-metric">
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Accuracy</span>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
              {metrics.accuracy_pct.toFixed(2)}%
            </div>
          </div>
          <div data-testid="signals-count">
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Signals</span>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
              {metrics.total_signals}
            </div>
          </div>
          <div data-testid="avg-return">
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Avg Return</span>
            <div
              style={{
                fontSize: 18,
                fontWeight: 700,
                color: metrics.avg_return >= 0 ? '#22c55e' : '#ef4444',
              }}
            >
              {metrics.avg_return >= 0 ? '+' : ''}
              {metrics.avg_return.toFixed(2)}%
            </div>
          </div>
        </div>
      )}

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <th
                style={{
                  textAlign: 'left',
                  padding: '8px 12px',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                }}
              >
                Symbol
              </th>
              <th
                style={{
                  textAlign: 'left',
                  padding: '8px 12px',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                }}
              >
                Stance
              </th>
              <th
                style={{
                  textAlign: 'left',
                  padding: '8px 12px',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                }}
              >
                Window
              </th>
              <th
                style={{
                  textAlign: 'left',
                  padding: '8px 12px',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                }}
              >
                Return
              </th>
              <th
                style={{
                  textAlign: 'left',
                  padding: '8px 12px',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                }}
              >
                Result
              </th>
            </tr>
          </thead>
          <tbody>
            {outcomes.map((outcome) => (
              <tr
                key={outcome.id}
                style={{ borderBottom: '1px solid var(--border)' }}
              >
                <td style={{ padding: '8px 12px', color: 'var(--text-primary)' }}>
                  {outcome.symbol}
                </td>
                <td
                  style={{
                    padding: '8px 12px',
                    color: 'var(--text-primary)',
                    textTransform: 'capitalize',
                  }}
                >
                  {outcome.stance}
                </td>
                <td style={{ padding: '8px 12px', color: 'var(--text-primary)' }}>
                  {outcome.window}
                </td>
                <td
                  style={{
                    padding: '8px 12px',
                    color: outcome.return_pct >= 0 ? '#22c55e' : '#ef4444',
                    fontWeight: 600,
                  }}
                >
                  {outcome.return_pct >= 0 ? '+' : ''}
                  {outcome.return_pct.toFixed(2)}%
                </td>
                <td style={{ padding: '8px 12px' }}>
                  <span
                    style={{
                      display: 'inline-block',
                      padding: '2px 8px',
                      borderRadius: 4,
                      fontSize: 12,
                      fontWeight: 600,
                      background: outcome.correct ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                      color: outcome.correct ? '#22c55e' : '#ef4444',
                    }}
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
