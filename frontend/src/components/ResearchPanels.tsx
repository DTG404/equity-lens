'use client';

import React, { useEffect, useState } from 'react';
import { fetchFundamentals, fetchTechnicals, type FundamentalsData, type TechnicalsData } from '@/lib/api';

interface ResearchDataPanelProps {
  symbol: string;
}

function formatLargeNum(n: number | null): string {
  if (n === null || n === undefined) return '—';
  if (Math.abs(n) >= 1e12) return `${(n / 1e12).toFixed(2)}T`;
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
  return n.toLocaleString();
}

export function FundamentalsPanel({ symbol }: ResearchDataPanelProps) {
  const [data, setData] = useState<FundamentalsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFundamentals(symbol)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [symbol]);

  if (error) return <p className="text-xs text-red-400">{error}</p>;
  if (!data) return <div className="h-24 animate-pulse rounded-lg bg-white/[0.03]" />;

  return (
    <div className="glass-panel p-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-white/40">Fundamentals</h3>
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <div className="mb-2 font-semibold text-white/50">Income</div>
          <div className="space-y-1.5 font-mono text-[0.65rem]">
            <div className="flex justify-between"><span className="text-white/30">Revenue</span><span className="text-[#f0f6fc]">{formatLargeNum(data.income_statement.revenue)}</span></div>
            <div className="flex justify-between"><span className="text-white/30">Net Income</span><span className="text-[#f0f6fc]">{formatLargeNum(data.income_statement.net_income)}</span></div>
            <div className="flex justify-between"><span className="text-white/30">Gross Margin</span><span className={data.ratios.gross_margin && data.ratios.gross_margin > 40 ? 'text-green-400' : 'text-[#f0f6fc]'}>{data.ratios.gross_margin ?? '—'}%</span></div>
            <div className="flex justify-between"><span className="text-white/30">Net Margin</span><span className={data.ratios.net_margin && data.ratios.net_margin > 15 ? 'text-green-400' : 'text-[#f0f6fc]'}>{data.ratios.net_margin ?? '—'}%</span></div>
          </div>
        </div>
        <div>
          <div className="mb-2 font-semibold text-white/50">Balance Sheet</div>
          <div className="space-y-1.5 font-mono text-[0.65rem]">
            <div className="flex justify-between"><span className="text-white/30">Assets</span><span className="text-[#f0f6fc]">{formatLargeNum(data.balance_sheet.total_assets)}</span></div>
            <div className="flex justify-between"><span className="text-white/30">Equity</span><span className="text-[#f0f6fc]">{formatLargeNum(data.balance_sheet.equity)}</span></div>
            <div className="flex justify-between"><span className="text-white/30">D/E</span><span className={data.ratios.debt_to_equity && data.ratios.debt_to_equity < 1 ? 'text-green-400' : 'text-amber-400'}>{data.ratios.debt_to_equity ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-white/30">Current Ratio</span><span className={data.ratios.current_ratio && data.ratios.current_ratio > 1.5 ? 'text-green-400' : 'text-amber-400'}>{data.ratios.current_ratio ?? '—'}</span></div>
          </div>
        </div>
      </div>
      {data.cash_flow.free_cash_flow && (
        <div className="mt-2 border-t border-white/[0.04] pt-2 font-mono text-[0.65rem]">
          <span className="text-white/30">Free Cash Flow: </span>
          <span className="text-[#f0f6fc]">{formatLargeNum(data.cash_flow.free_cash_flow)}</span>
        </div>
      )}
    </div>
  );
}

export function TechnicalsPanel({ symbol }: ResearchDataPanelProps) {
  const [data, setData] = useState<TechnicalsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTechnicals(symbol)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [symbol]);

  if (error) return <p className="text-xs text-red-400">{error}</p>;
  if (!data) return <div className="h-24 animate-pulse rounded-lg bg-white/[0.03]" />;

  const rsiColor = data.rsi !== null ? (data.rsi > 70 ? 'text-red-400' : data.rsi < 30 ? 'text-green-400' : 'text-[#f0f6fc]') : 'text-white/30';

  return (
    <div className="glass-panel p-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-white/40">Technicals</h3>
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <div className="mb-2 font-semibold text-white/50">Momentum</div>
          <div className="space-y-1.5 font-mono text-[0.65rem]">
            <div className="flex justify-between"><span className="text-white/30">RSI (14)</span><span className={rsiColor}>{data.rsi?.toFixed(1) ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-white/30">MACD</span><span className={data.macd.macd_line !== null ? (data.macd.macd_line > 0 ? 'text-green-400' : 'text-red-400') : 'text-white/30'}>{data.macd.macd_line?.toFixed(2) ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-white/30">Signal</span><span className="text-white/60">{data.macd.signal_line?.toFixed(2) ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-white/30">ATR (14)</span><span className="text-[#f0f6fc]">{data.atr?.toFixed(2) ?? '—'}</span></div>
          </div>
        </div>
        <div>
          <div className="mb-2 font-semibold text-white/50">Moving Averages</div>
          <div className="space-y-1.5 font-mono text-[0.65rem]">
            <div className="flex justify-between"><span className="text-white/30">SMA 20</span><span className="text-[#f0f6fc]">{data.moving_averages.sma_20?.toFixed(2) ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-white/30">SMA 50</span><span className="text-[#f0f6fc]">{data.moving_averages.sma_50?.toFixed(2) ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-white/30">SMA 200</span><span className="text-[#f0f6fc]">{data.moving_averages.sma_200?.toFixed(2) ?? '—'}</span></div>
            <div className="flex justify-between"><span className="text-white/30">BB Upper</span><span className="text-cyan-400">{data.bollinger_bands.upper?.toFixed(2) ?? '—'}</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
