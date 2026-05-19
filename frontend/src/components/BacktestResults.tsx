'use client';

import React from 'react';
import { BacktestResult } from '@/lib/api';

interface Props {
  result: BacktestResult;
}

export default function BacktestResults({ result }: Props) {
  if (result.total_trades === 0) {
    return (
      <div className="glass-panel p-4">
        <p className="text-xs text-white/30">No trades generated. Try different conditions.</p>
      </div>
    );
  }

  const vsBuyHold = result.overall_return_pct - result.buy_hold_return_pct;

  return (
    <div className="glass-panel p-4 space-y-4">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-white/40">
        {result.strategy_name} — Results
      </h2>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total Trades', value: result.total_trades.toString(), color: 'text-white/70' },
          { label: 'Win Rate', value: `${(result.win_rate * 100).toFixed(1)}%`, color: result.win_rate >= 0.5 ? 'text-green-400' : 'text-red-400' },
          { label: 'Return', value: `${result.overall_return_pct >= 0 ? '+' : ''}${result.overall_return_pct.toFixed(1)}%`, color: result.overall_return_pct >= 0 ? 'text-green-400' : 'text-red-400' },
          { label: 'vs Buy & Hold', value: `${vsBuyHold >= 0 ? '+' : ''}${vsBuyHold.toFixed(1)}%`, color: vsBuyHold >= 0 ? 'text-green-400' : 'text-red-400' },
        ].map(item => (
          <div key={item.label} className="text-center">
            <div className={`text-lg font-bold font-mono ${item.color}`}>{item.value}</div>
            <div className="text-[0.55rem] uppercase text-white/30 mt-1">{item.label}</div>
          </div>
        ))}
      </div>

      {result.results.map(r => r.trades_list && r.trades_list.length > 0 && (
        <div key={r.symbol}>
          <h3 className="text-[0.6rem] uppercase text-white/30 mb-2">{r.symbol} — {r.trades} trades</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-[0.6rem]">
              <thead>
                <tr className="text-white/30 border-b border-white/[0.04]">
                  <th className="text-left pr-2 py-1">Entry</th>
                  <th className="text-left pr-2 py-1">Exit</th>
                  <th className="text-right px-2 py-1">Entry $</th>
                  <th className="text-right px-2 py-1">Exit $</th>
                  <th className="text-right px-2 py-1">Return</th>
                  <th className="text-right px-2 py-1">Bars</th>
                </tr>
              </thead>
              <tbody>
                {r.trades_list.slice(0, 10).map((t, i) => (
                  <tr key={i} className="border-b border-white/[0.02]">
                    <td className="pr-2 py-1 text-white/50">{t.entry_date}</td>
                    <td className="pr-2 py-1 text-white/50">{t.exit_date}</td>
                    <td className="text-right px-2 py-1 font-mono text-white/60">${t.entry_price.toFixed(2)}</td>
                    <td className="text-right px-2 py-1 font-mono text-white/60">${t.exit_price.toFixed(2)}</td>
                    <td className={`text-right px-2 py-1 font-mono ${t.return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {t.return_pct >= 0 ? '+' : ''}{t.return_pct.toFixed(2)}%
                    </td>
                    <td className="text-right px-2 py-1 font-mono text-white/40">{t.bars_held}</td>
                  </tr>
                ))}
                {r.trades_list.length > 10 && (
                  <tr><td colSpan={6} className="text-center text-white/20 py-1">+{r.trades_list.length - 10} more</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
