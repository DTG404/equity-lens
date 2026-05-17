'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  fetchWatchlist,
  fetchHoldings,
  fetchNews,
  addToWatchlist,
  removeFromWatchlist,
  addHolding,
  type WatchlistItem,
  type HoldingItem,
  type NewsArticle,
} from '@/lib/api';
import AlertCenter from '@/components/AlertCenter';

function WatchlistCard({
  item,
  onRemove,
}: {
  item: WatchlistItem;
  onRemove: (symbol: string) => void;
}) {
  const changeColor =
    item.change_percent === null || item.change_percent === 0
      ? 'var(--text-secondary)'
      : item.change_percent > 0
        ? '#22c55e'
        : '#ef4444';

  const changeSign =
    item.change_percent === null || item.change_percent === 0
      ? ''
      : item.change_percent > 0
        ? '+'
        : '';

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        borderRadius: 8,
        padding: 16,
        border: '1px solid var(--border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}
    >
      <div>
        <Link
          href={`/stocks/${item.symbol}`}
          style={{
            fontSize: 18,
            fontWeight: 700,
            color: 'var(--text-primary)',
            textDecoration: 'none',
            display: 'block',
          }}
        >
          {item.symbol}
        </Link>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          {item.company_name}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 15, fontWeight: 600 }}>
            {item.price !== null ? `$${item.price.toFixed(2)}` : '—'}
          </div>
          <div style={{ fontSize: 12, color: changeColor }}>
            {item.change_percent !== null
              ? `${changeSign}${item.change_percent.toFixed(2)}%`
              : '—'}
          </div>
        </div>
        <button
          type="button"
          onClick={() => onRemove(item.symbol)}
          style={{
            background: 'transparent',
            border: '1px solid var(--border)',
            borderRadius: 4,
            padding: '4px 12px',
            fontSize: 13,
            cursor: 'pointer',
            color: 'var(--text-secondary)',
          }}
        >
          Remove
        </button>
      </div>
    </div>
  );
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

function NewsArticleCard({ article }: { article: NewsArticle }) {
  return (
    <div
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
  );
}

function HoldingRow({ holding }: { holding: HoldingItem }) {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 0',
        borderBottom: '1px solid var(--border)',
      }}
    >
      <span style={{ fontWeight: 600 }}>{holding.symbol}</span>
      <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
        {holding.quantity} @ ${holding.average_cost.toFixed(2)}
      </span>
    </div>
  );
}

export default function DashboardShell() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [holdings, setHoldings] = useState<HoldingItem[]>([]);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [newTicker, setNewTicker] = useState('');
  const [holdingSymbol, setHoldingSymbol] = useState('');
  const [holdingQuantity, setHoldingQuantity] = useState('');
  const [holdingCost, setHoldingCost] = useState('');

  useEffect(() => {
    fetchWatchlist()
      .then(setWatchlist)
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    fetchHoldings()
      .then(setHoldings)
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    if (watchlist.length > 0) {
      fetchNews(watchlist[0].symbol)
        .then(setNews)
        .catch((err: Error) => setError(err.message));
    } else {
      fetchNews()
        .then(setNews)
        .catch((err: Error) => setError(err.message));
    }
  }, [watchlist]);

  const handleAddTicker = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicker.trim()) return;
    try {
      await addToWatchlist(newTicker.trim().toUpperCase());
      setNewTicker('');
      const updated = await fetchWatchlist();
      setWatchlist(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add ticker');
    }
  };

  const handleRemoveTicker = async (symbol: string) => {
    try {
      await removeFromWatchlist(symbol);
      const updated = await fetchWatchlist();
      setWatchlist(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove ticker');
    }
  };

  const handleAddHolding = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!holdingSymbol.trim() || !holdingQuantity || !holdingCost) return;
    try {
      await addHolding(
        holdingSymbol.trim().toUpperCase(),
        parseFloat(holdingQuantity),
        parseFloat(holdingCost),
      );
      setHoldingSymbol('');
      setHoldingQuantity('');
      setHoldingCost('');
      const updated = await fetchHoldings();
      setHoldings(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add holding');
    }
  };

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 16px' }}>
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700 }}>Equity Lens</h1>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginTop: 4 }}>
          Local-first research terminal
        </p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <section style={{ gridColumn: '1 / -1' }}>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Watchlist</h2>

          <form
            onSubmit={handleAddTicker}
            style={{ display: 'flex', gap: 8, marginBottom: 16 }}
          >
            <input
              type="text"
              placeholder="Ticker symbol"
              value={newTicker}
              onChange={(e) => setNewTicker(e.target.value)}
              style={{
                flex: 1,
                padding: '8px 12px',
                borderRadius: 4,
                border: '1px solid var(--border)',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: 14,
              }}
            />
            <button
              type="submit"
              style={{
                padding: '8px 16px',
                borderRadius: 4,
                border: 'none',
                background: 'var(--accent-blue, #3b82f6)',
                color: '#fff',
                fontSize: 14,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Add
            </button>
          </form>

          {error && (
            <p style={{ color: 'var(--accent-red)', fontSize: 14 }}>
              Could not load watchlist: {error}
            </p>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {watchlist.map((item) => (
              <WatchlistCard
                key={item.symbol}
                item={item}
                onRemove={handleRemoveTicker}
              />
            ))}
          </div>
        </section>

        <section
          style={{
            background: 'var(--bg-secondary)',
            borderRadius: 8,
            padding: 16,
            border: '1px solid var(--border)',
            minHeight: 120,
          }}
        >
          <AlertCenter />
        </section>

        <section
          style={{
            background: 'var(--bg-secondary)',
            borderRadius: 8,
            padding: 16,
            border: '1px solid var(--border)',
            minHeight: 120,
          }}
        >
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Holdings</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {holdings.map((holding) => (
              <HoldingRow key={holding.id} holding={holding} />
            ))}
          </div>

          <form
            onSubmit={handleAddHolding}
            style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 12 }}
          >
            <input
              type="text"
              placeholder="Symbol"
              value={holdingSymbol}
              onChange={(e) => setHoldingSymbol(e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: 4,
                border: '1px solid var(--border)',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: 13,
              }}
            />
            <input
              type="number"
              placeholder="Quantity"
              value={holdingQuantity}
              onChange={(e) => setHoldingQuantity(e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: 4,
                border: '1px solid var(--border)',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: 13,
              }}
            />
            <input
              type="number"
              placeholder="Avg cost"
              value={holdingCost}
              onChange={(e) => setHoldingCost(e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: 4,
                border: '1px solid var(--border)',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: 13,
              }}
            />
            <button
              type="submit"
              style={{
                padding: '6px 12px',
                borderRadius: 4,
                border: 'none',
                background: 'var(--accent-blue, #3b82f6)',
                color: '#fff',
                fontSize: 13,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Add Holding
            </button>
          </form>
        </section>

        <section style={{ gridColumn: '1 / -1' }}>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>News Feed</h2>
          <div
            style={{
              background: 'var(--bg-secondary)',
              borderRadius: 8,
              padding: 16,
              border: '1px solid var(--border)',
            }}
          >
            {news.length === 0 ? (
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                No recent news.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {news.slice(0, 5).map((article) => (
                  <NewsArticleCard key={article.id} article={article} />
                ))}
              </div>
            )}
          </div>
        </section>
      </div>

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
