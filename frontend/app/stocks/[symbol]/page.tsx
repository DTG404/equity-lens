'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { fetchResearch, type ResearchData } from '@/lib/api';
import PriceChart from '@/components/PriceChart';
import FactorScoreCard from '@/components/FactorScoreCard';
import ScenarioCard from '@/components/ScenarioCard';
import SignalHistory from '@/components/SignalHistory';

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

  const loadResearch = useCallback(async () => {
    try {
      const resolved = await params;
      const sym = resolved.symbol.toUpperCase();
      setSymbol(sym);
      const research = await fetchResearch(sym);
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
        const research = await fetchResearch(sym);
        if (!cancelled) {
          setData(research);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load research');
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [params]);

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    await loadResearch();
    setIsRegenerating(false);
  };

  const changeColor =
    !data?.quote || data.quote.change_percent === 0
      ? 'var(--text-secondary)'
      : data.quote.change_percent > 0
        ? '#22c55e'
        : '#ef4444';

  const changeSign =
    !data?.quote || data.quote.change_percent === 0
      ? ''
      : data.quote.change_percent > 0
        ? '+'
        : '';

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 16px' }}>
      <div style={{ marginBottom: 24 }}>
        <Link
          href="/"
          style={{
            fontSize: 14,
            color: 'var(--text-secondary)',
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
          }}
        >
          <span>←</span>
          <span>Back to Dashboard</span>
        </Link>
      </div>

      {error && (
        <p style={{ color: 'var(--accent-red)', fontSize: 14, marginBottom: 16 }}>
          {error}
        </p>
      )}

      {data && (
        <>
          <header style={{ marginBottom: 32 }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'baseline',
                gap: 16,
                flexWrap: 'wrap',
              }}
            >
              <h1 style={{ fontSize: 32, fontWeight: 800, margin: 0 }}>
                {symbol}
              </h1>
              {data.quote && (
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                  <span style={{ fontSize: 24, fontWeight: 700 }}>
                    ${data.quote.price.toFixed(2)}
                  </span>
                  <span
                    style={{
                      fontSize: 16,
                      fontWeight: 600,
                      color: changeColor,
                    }}
                  >
                    {changeSign}
                    {data.quote.change_percent.toFixed(2)}%
                  </span>
                </div>
              )}
            </div>
          </header>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 24,
              marginBottom: 32,
            }}
          >
            <section style={{ gridColumn: '1 / -1' }}>
              <h2
                style={{
                  fontSize: 18,
                  fontWeight: 600,
                  marginBottom: 12,
                }}
              >
                Price History
              </h2>
              <div
                style={{
                  background: 'var(--bg-card)',
                  borderRadius: 8,
                  padding: 16,
                  border: '1px solid var(--border)',
                }}
              >
                <PriceChart
                  data={data.price_history.map((h) => ({
                    date: h.date,
                    close: h.close,
                  }))}
                />
              </div>
            </section>

            <section style={{ gridColumn: '1 / -1' }}>
              <h2
                style={{
                  fontSize: 18,
                  fontWeight: 600,
                  marginBottom: 12,
                }}
              >
                Factor Analysis
              </h2>
              <FactorScoreCard scores={data.scores} />
            </section>

            <section style={{ gridColumn: '1 / -1' }}>
              <h2
                style={{
                  fontSize: 18,
                  fontWeight: 600,
                  marginBottom: 12,
                }}
              >
                News
              </h2>
              <div
                style={{
                  background: 'var(--bg-card)',
                  borderRadius: 8,
                  padding: 16,
                  border: '1px solid var(--border)',
                }}
              >
                {data.news.length === 0 ? (
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                    No recent news.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    {data.news.map((article) => (
                      <div
                        key={article.id}
                        style={{
                          padding: '10px 0',
                          borderBottom: '1px solid var(--border)',
                        }}
                      >
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontSize: 14,
                            fontWeight: 600,
                            color: 'var(--text-primary)',
                            textDecoration: 'none',
                            display: 'block',
                            marginBottom: 4,
                          }}
                        >
                          {article.title}
                        </a>
                        <div
                          style={{
                            fontSize: 12,
                            color: 'var(--text-secondary)',
                            display: 'flex',
                            justifyContent: 'space-between',
                          }}
                        >
                          <span>{article.source}</span>
                          <span>{formatRelativeTime(article.published_at)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

            <section style={{ gridColumn: '1 / -1' }}>
              <h2
                style={{
                  fontSize: 18,
                  fontWeight: 600,
                  marginBottom: 12,
                }}
              >
                Thesis
              </h2>
              <div
                style={{
                  background: 'var(--bg-card)',
                  borderRadius: 8,
                  padding: 16,
                  border: '1px solid var(--border)',
                  fontSize: 14,
                  lineHeight: 1.6,
                }}
              >
                {data.thesis}
              </div>
            </section>

            <section style={{ gridColumn: '1 / -1' }}>
              <h2
                style={{
                  fontSize: 18,
                  fontWeight: 600,
                  marginBottom: 12,
                }}
              >
                Scenarios
              </h2>
              <ScenarioCard
                bullCase={data.scenarios.bull_case}
                baseCase={data.scenarios.base_case}
                bearCase={data.scenarios.bear_case}
              />
            </section>

            <section style={{ gridColumn: '1 / -1' }}>
              <h2
                style={{
                  fontSize: 18,
                  fontWeight: 600,
                  marginBottom: 12,
                }}
              >
                Signal History
              </h2>
              <SignalHistory symbol={symbol} />
            </section>

            <section style={{ gridColumn: '1 / -1' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 12,
                  marginBottom: 12,
                }}
              >
                <h2
                  style={{
                    fontSize: 18,
                    fontWeight: 600,
                    margin: 0,
                  }}
                >
                  Risks
                </h2>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    flexWrap: 'wrap',
                  }}
                >
                  <span
                    style={{
                      fontSize: 12,
                      color: 'var(--text-secondary)',
                    }}
                  >
                    Model: {data.scenarios.model}
                  </span>
                  <span
                    style={{
                      fontSize: 12,
                      color: 'var(--text-secondary)',
                    }}
                  >
                    Analysis #{data.analysis_id}
                  </span>
                  <button
                    onClick={handleRegenerate}
                    disabled={isRegenerating}
                    style={{
                      fontSize: 12,
                      fontWeight: 600,
                      padding: '6px 12px',
                      borderRadius: 6,
                      border: '1px solid var(--border)',
                      background: 'var(--bg-card)',
                      color: 'var(--text-primary)',
                      cursor: isRegenerating ? 'not-allowed' : 'pointer',
                      opacity: isRegenerating ? 0.6 : 1,
                    }}
                  >
                    {isRegenerating ? 'Regenerating...' : 'Regenerate Analysis'}
                  </button>
                </div>
              </div>
              <div
                style={{
                  background: 'var(--bg-card)',
                  borderRadius: 8,
                  padding: 16,
                  border: '1px solid var(--border)',
                  fontSize: 14,
                  lineHeight: 1.6,
                }}
              >
                {data.risks}
              </div>
            </section>
          </div>
        </>
      )}

      <footer
        style={{
          marginTop: 48,
          padding: 16,
          borderTop: '1px solid var(--border)',
          fontSize: 12,
          color: 'var(--text-secondary)',
          textAlign: 'center',
        }}
      >
        This is a local research tool. No trades are executed. All data is for
        informational purposes only.
      </footer>
    </div>
  );
}
