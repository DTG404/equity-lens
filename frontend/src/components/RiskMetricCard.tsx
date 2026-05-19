'use client';

import { RiskMetrics } from '@/lib/api';

interface Props {
  metrics: RiskMetrics | null;
}

function formatNum(v: number | null, decimals = 2): string {
  if (v === null || v === undefined) return '—';
  return v.toFixed(decimals);
}

export default function RiskMetricCard({ metrics }: Props) {
  if (!metrics) {
    return (
      <div className="glass-panel p-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-3">Risk Metrics</h3>
        <p className="text-xs text-white/30">Add holdings and price data to see risk metrics.</p>
      </div>
    );
  }

  const items = [
    { label: 'Sharpe Ratio', value: formatNum(metrics.sharpe_ratio), color: (metrics.sharpe_ratio ?? 0) >= 1 ? 'text-green-400' : (metrics.sharpe_ratio ?? 0) >= 0.5 ? 'text-amber-400' : 'text-red-400', tooltip: 'Risk-adjusted return. >1 = good, >2 = great' },
    { label: 'Alpha', value: `${metrics.alpha_pct !== null && metrics.alpha_pct >= 0 ? '+' : ''}${formatNum(metrics.alpha_pct)}%`, color: (metrics.alpha_pct ?? 0) >= 0 ? 'text-green-400' : 'text-red-400', tooltip: 'Excess return vs benchmark' },
    { label: 'Beta', value: formatNum(metrics.beta, 2), color: 'text-cyan-400', tooltip: `${metrics.beta !== null && metrics.beta > 1 ? 'More' : 'Less'} volatile than market (S&P 500 = 1.0)` },
    { label: 'Max Drawdown', value: formatNum(metrics.max_drawdown_pct) + '%', color: 'text-red-400', tooltip: 'Largest peak-to-trough decline' },
    { label: 'Volatility (Ann.)', value: formatNum(metrics.volatility_annualized_pct) + '%', color: 'text-amber-400', tooltip: 'Annualized standard deviation of returns' },
  ];

  return (
    <div className="glass-panel p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-3">Risk Metrics</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {items.map((item) => (
          <div key={item.label} className="text-center" title={item.tooltip}>
            <div className={`text-lg font-bold font-mono ${item.color}`}>{item.value}</div>
            <div className="text-[0.6rem] uppercase tracking-wider text-white/30 mt-1">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
