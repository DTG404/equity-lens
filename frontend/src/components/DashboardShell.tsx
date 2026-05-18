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
    <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
      {/* ── Watchlist Section (2 cols) ── */}
      <section className="lg:col-span-2">
        <div className="glass-panel animate-fade-in overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-white/[0.04] px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider gradient-text">
              Watchlist
            </h2>
            <span className="font-mono text-[0.55rem] text-white/20">
              {watchlist.length} symbols
            </span>
          </div>

          {/* Add form */}
          <form onSubmit={handleAddTicker} className="flex gap-2 border-b border-white/[0.04] px-4 py-3">
            <input
              type="text"
              placeholder="Ticker symbol"
              value={newTicker}
              onChange={(e) => setNewTicker(e.target.value)}
              className="flex-1 rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#f0f6fc] placeholder-white/25 outline-none transition-colors focus:border-cyan-400/30"
            />
            <button
              type="submit"
              className="glass-badge-cyan inline-flex items-center rounded-lg px-4 py-2 text-xs font-semibold uppercase tracking-wider transition-opacity hover:opacity-80"
            >
              Add
            </button>
          </form>

          {/* Error */}
          {error && (
            <div className="border-b border-white/[0.04] px-4 py-2">
              <p className="text-xs text-red-400">Could not load watchlist: {error}</p>
            </div>
          )}

          {/* Table header */}
          {watchlist.length > 0 && (
            <div className="flex border-b border-white/[0.03] px-4 py-2 text-[0.6rem] font-medium uppercase tracking-wider text-white/30">
              <div className="flex-[2]">Symbol</div>
              <div className="flex-1 text-right">Price</div>
              <div className="flex-1 text-right">Change</div>
              <div className="flex-1 text-right">Signal</div>
              <div className="w-16 text-right" />
            </div>
          )}

          {/* Watchlist rows */}
          {watchlist.map((item) => {
            const changeColor =
              item.change_percent === null || item.change_percent === 0
                ? 'text-white/40'
                : item.change_percent > 0
                  ? 'text-green-400'
                  : 'text-red-400';
            const changeSign =
              item.change_percent === null || item.change_percent === 0
                ? ''
                : item.change_percent > 0
                  ? '+'
                  : '';
            const signal = item.signal ? { label: item.signal.toUpperCase(), cls: item.signal === 'bullish' ? 'glass-badge-green text-green-400' : item.signal === 'bearish' ? 'glass-badge-red text-red-400' : 'glass-badge-amber text-amber-400' } : null;
            return (
              <div
                key={item.symbol}
                className="flex items-center border-b border-white/[0.03] px-4 py-2.5 text-sm transition-colors last:border-0 hover:bg-white/[0.01]"
              >
                <div className="flex-[2]">
                  <Link
                    href={`/stocks/${item.symbol}`}
                    className="font-semibold text-[#f0f6fc] no-underline transition-colors hover:text-cyan-400"
                  >
                    {item.symbol}
                  </Link>
                  {item.company_name && (
                    <div className="text-xs text-white/40">{item.company_name}</div>
                  )}
                </div>
                <div className="flex-1 text-right font-mono text-xs text-[#f0f6fc]">
                  {item.price !== null ? `$${item.price.toFixed(2)}` : '—'}
                </div>
                <div className={`flex-1 text-right font-mono text-xs ${changeColor}`}>
                  {item.change_percent !== null
                    ? `${changeSign}${item.change_percent.toFixed(2)}%`
                    : '—'}
                </div>
                <div className="flex-1 text-right">
                  {signal && (
                    <span className={`inline-block rounded-full px-2 py-0.5 font-mono text-[0.6rem] ${signal.cls}`}>
                      {signal.label}
                    </span>
                  )}
                </div>
                <div className="w-16 text-right">
                  <button
                    type="button"
                    onClick={() => handleRemoveTicker(item.symbol)}
                    className="glass-badge-red inline-block rounded-full px-2 py-0.5 font-mono text-[0.6rem] transition-opacity hover:opacity-80"
                  >
                    ✕
                  </button>
                </div>
              </div>
            );
          })}

          {watchlist.length === 0 && !error && (
            <div className="px-4 py-6 text-center text-xs text-white/25">
              Add symbols to your watchlist above
            </div>
          )}
        </div>
      </section>

      {/* ── Right Column: Alerts + Holdings ── */}
      <section className="flex flex-col gap-3">
        {/* Alerts */}
        <div className="glass-panel overflow-hidden">
          <div className="border-b border-white/[0.04] px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider gradient-text">
              Alerts
            </h2>
          </div>
          <div className="p-3">
            <AlertCenter />
          </div>
        </div>

        {/* Holdings */}
        <div className="glass-panel overflow-hidden">
          <div className="border-b border-white/[0.04] px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider gradient-text">
              Holdings
            </h2>
          </div>
          <div className="p-3">
            {holdings.length === 0 ? (
              <p className="py-2 text-xs text-white/25">No holdings yet</p>
            ) : (
              <>
                <div className="flex border-b border-white/[0.03] px-2 py-2 text-[0.6rem] font-medium uppercase tracking-wider text-white/30">
                  <div className="flex-[2]">Symbol</div>
                  <div className="flex-1 text-right">Qty</div>
                  <div className="flex-1 text-right">Cost</div>
                </div>
                <div className="mb-3">
                  {holdings.map((holding) => (
                    <div
                      key={holding.id}
                      className="flex items-center border-b border-white/[0.03] px-2 py-2.5 text-sm last:border-0 transition-colors hover:bg-white/[0.01]"
                    >
                      <div className="flex-[2] font-mono text-sm font-semibold text-[#f0f6fc]">
                        {holding.symbol}
                      </div>
                      <div className="flex-1 text-right font-mono text-xs text-[#f0f6fc]">
                        {holding.quantity}
                      </div>
                      <div className="flex-1 text-right font-mono text-xs text-white/40">
                        ${holding.average_cost.toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            <form onSubmit={handleAddHolding} className="flex flex-col gap-2">
              <input
                type="text"
                placeholder="Symbol"
                value={holdingSymbol}
                onChange={(e) => setHoldingSymbol(e.target.value)}
                className="w-full rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#f0f6fc] placeholder-white/25 outline-none transition-colors focus:border-cyan-400/30"
              />
              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="Qty"
                  value={holdingQuantity}
                  onChange={(e) => setHoldingQuantity(e.target.value)}
                  className="w-1/2 rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#f0f6fc] placeholder-white/25 outline-none transition-colors focus:border-cyan-400/30"
                />
                <input
                  type="number"
                  placeholder="Cost"
                  value={holdingCost}
                  onChange={(e) => setHoldingCost(e.target.value)}
                  className="w-1/2 rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#f0f6fc] placeholder-white/25 outline-none transition-colors focus:border-cyan-400/30"
                />
              </div>
              <button
                type="submit"
                className="glass-badge-cyan inline-flex items-center justify-center w-full rounded-lg px-4 py-2 text-xs font-semibold uppercase tracking-wider transition-opacity hover:opacity-80"
              >
                Add Holding
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* ── News Feed (full width below) ── */}
      <section className="lg:col-span-3">
        <div className="glass-panel overflow-hidden">
          <div className="flex items-center justify-between border-b border-white/[0.04] px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider gradient-text">
              News Feed
            </h2>
            {news.length > 0 && (
              <span className="font-mono text-[0.55rem] text-white/20">
                Latest {Math.min(news.length, 5)} articles
              </span>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto px-4 py-2">
            {news.length === 0 ? (
              <p className="py-3 text-center text-xs text-white/25">No recent news.</p>
            ) : (
              <div>
                {news.slice(0, 5).map((article) => (
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
                      <span className="text-white/25">{formatRelativeTime(article.published_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
