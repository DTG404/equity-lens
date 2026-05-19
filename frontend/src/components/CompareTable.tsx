'use client';

import React from 'react';

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

const METRIC_LABELS: Record<string, string> = {
  price: 'Price',
  change_pct: 'Change %',
  market_cap: 'Market Cap',
  pe_ratio: 'P/E Ratio',
  revenue_growth: 'Rev Growth %',
  profit_margin: 'Profit Margin %',
  rsi: 'RSI (14)',
  sector: 'Sector',
};

const METRIC_KEYS = [
  'price',
  'change_pct',
  'market_cap',
  'pe_ratio',
  'revenue_growth',
  'profit_margin',
  'rsi',
  'sector',
];

function formatValue(key: string, value: number | string): string {
  if (value === 0 || value === 'Unknown') return '—';
  if (key === 'price') return `$${Number(value).toFixed(2)}`;
  if (key === 'market_cap') {
    const v = Number(value);
    if (v >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
    if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
    if (v >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
    return `$${(v / 1e3).toFixed(1)}K`;
  }
  if (key === 'change_pct' || key === 'revenue_growth' || key === 'profit_margin') {
    const v = Number(value);
    return `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`;
  }
  if (key === 'rsi') return Number(value).toFixed(1);
  if (key === 'pe_ratio') return Number(value).toFixed(1);
  return String(value);
}

function valueColor(key: string, value: number | string): string {
  if (key === 'change_pct') {
    const v = Number(value);
    if (v > 0) return 'text-green-400';
    if (v < 0) return 'text-red-400';
    return 'text-[#f0f6fc]';
  }
  if (key === 'rsi') {
    const v = Number(value);
    if (v > 70) return 'text-red-400';
    if (v < 30) return 'text-green-400';
    return 'text-[#f0f6fc]';
  }
  return 'text-[#f0f6fc]';
}

export default function CompareTable({ data }: { data: CompareData }) {
  if (!data || !data.tickers?.length) {
    return (
      <div className="px-4 py-8 text-center text-xs text-white/25">
        No comparison data available
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-xs">
        <thead>
          <tr className="border-b border-white/[0.03] text-[0.6rem] uppercase tracking-wider text-white/25">
            <th className="px-3 py-2 text-left font-medium">Metric</th>
            {data.tickers.map((ticker) => (
              <th key={ticker} className="px-3 py-2 text-right font-medium">
                {ticker}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {METRIC_KEYS.map((key) => (
            <tr
              key={key}
              className="border-b border-white/[0.02] font-mono text-[0.65rem] last:border-0 hover:bg-white/[0.01]"
            >
              <td className="px-3 py-2 text-white/40">{METRIC_LABELS[key]}</td>
              {data.tickers.map((ticker) => {
                const raw = data.metrics[ticker]?.[key as keyof CompareMetrics];
                const formatted = formatValue(key, raw ?? 0);
                const color = valueColor(key, raw ?? 0);
                const isBest =
                  key !== 'sector' &&
                  data.best_values[key] === ticker &&
                  raw !== 0 &&
                  raw !== 'Unknown';
                return (
                  <td
                    key={ticker}
                    className={`px-3 py-2 text-right ${color} ${
                      isBest ? 'bg-green-500/10' : ''
                    }`}
                  >
                    {formatted}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
