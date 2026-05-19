'use client';

import React, { useState, useEffect } from 'react';
import { fetchPatterns, type DetectedPattern } from '@/lib/api';

interface Props {
  symbol: string;
}

const PATTERN_LABELS: Record<string, string> = {
  double_top: 'Double Top',
  double_bottom: 'Double Bottom',
  bull_flag: 'Bull Flag',
  hammer: 'Hammer',
  shooting_star: 'Shooting Star',
};

const PATTERN_ICONS: Record<string, string> = {
  double_top: '↥',
  double_bottom: '↧',
  bull_flag: '⚑',
  hammer: '⌐',
  shooting_star: '★',
};

export default function PatternPanel({ symbol }: Props) {
  const [patterns, setPatterns] = useState<DetectedPattern[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchPatterns(symbol)
      .then((data) => setPatterns(data.patterns))
      .catch(() => setPatterns([]))
      .finally(() => setLoading(false));
  }, [symbol]);

  const bullish = patterns.filter((p) => p.direction === 'bullish');
  const bearish = patterns.filter((p) => p.direction === 'bearish');

  return (
    <div className="glass-panel p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-3">
        Chart Patterns
      </h3>
      {loading && (
        <div className="animate-pulse space-y-2">
          <div className="h-3 bg-white/5 rounded w-1/2" />
          <div className="h-3 bg-white/5 rounded w-2/3" />
        </div>
      )}
      {!loading && patterns.length === 0 && (
        <p className="text-xs text-white/30">No patterns detected.</p>
      )}
      {!loading && patterns.length > 0 && (
        <div className="space-y-1">
          {patterns.slice(0, 5).map((p, i) => (
            <div
              key={i}
              className="flex items-center gap-2 text-xs py-1 border-b border-white/[0.03] last:border-0"
            >
              <span className="text-sm">{PATTERN_ICONS[p.type] || '⟡'}</span>
              <span className="flex-1 text-white/70">
                {PATTERN_LABELS[p.type] || p.type.replace(/_/g, ' ')}
              </span>
              <span
                className={`text-[0.55rem] font-semibold ${
                  p.direction === 'bullish' ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {p.direction === 'bullish' ? '▲' : '▼'} {p.direction}
              </span>
              <span className="text-white/30 text-[0.55rem]">
                {Math.round(p.confidence * 100)}%
              </span>
              <span className="text-white/30 text-[0.55rem] font-mono">
                → ${p.target_price}
              </span>
            </div>
          ))}
          {patterns.length > 5 && (
            <p className="text-[0.55rem] text-white/30 text-center pt-1">
              +{patterns.length - 5} more
            </p>
          )}
          <div className="flex gap-3 mt-2 pt-2 border-t border-white/[0.04] text-[0.55rem]">
            <span className="text-green-400">▲ {bullish.length} bullish</span>
            <span className="text-red-400">▼ {bearish.length} bearish</span>
          </div>
        </div>
      )}
    </div>
  );
}
