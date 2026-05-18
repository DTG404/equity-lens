'use client';

import React, { useEffect, useState } from 'react';
import { fetchPortfolioPerformance, fetchSignalMetrics, fetchMacro, fetchUnreadAlertCount } from '@/lib/api';

interface KpiData {
  portfolioValue: string | null;
  portfolioChange: string | null;
  signalAccuracy: string | null;
  signalTrend: string | null;
  alertCount: number | null;
  criticalAlerts: boolean;
  sp500: string | null;
  vix: string | null;
}

export default function KpiStrip() {
  const [data, setData] = useState<KpiData>({
    portfolioValue: null,
    portfolioChange: null,
    signalAccuracy: null,
    signalTrend: null,
    alertCount: null,
    criticalAlerts: false,
    sp500: null,
    vix: null,
  });

  useEffect(() => {
    async function load() {
      try {
        const [perf, metrics, macro, unread] = await Promise.all([
          fetchPortfolioPerformance().catch(() => null),
          fetchSignalMetrics().catch(() => null),
          fetchMacro().catch(() => null),
          fetchUnreadAlertCount().catch(() => null),
        ]);

        setData({
          portfolioValue: perf ? `$${(perf.total_value / 1000).toFixed(1)}k` : null,
          portfolioChange: perf ? `${perf.total_pl >= 0 ? '▲' : '▼'} ${perf.total_pl_pct.toFixed(2)}%` : null,
          signalAccuracy: metrics ? `${metrics.accuracy_pct.toFixed(1)}%` : null,
          signalTrend: metrics ? `${metrics.avg_return >= 0 ? '+' : ''}${metrics.avg_return.toFixed(2)}% avg` : null,
          alertCount: unread,
          criticalAlerts: false,
          sp500: (() => {
            const gdp = macro?.indicators?.GDP;
            return gdp && gdp.change !== null ? `${gdp.change >= 0 ? '+' : ''}${gdp.change}%` : null;
          })(),
          vix: null,
        });
      } catch { /* ignore */ }
    }
    load();
  }, []);

  return (
    <div className="mx-3 mt-2 flex gap-2">
      <KpiCard
        label="Portfolio Value"
        value={data.portfolioValue ?? '—'}
        subValue={data.portfolioChange ? undefined : 'Add holdings to see'}
        subColor={data.portfolioChange ? (data.portfolioChange.startsWith('▲') ? 'text-green-400' : 'text-red-400') : 'text-white/20'}
      >
        {data.portfolioChange && <div className={`font-mono text-xs ${data.portfolioChange.startsWith('▲') ? 'text-green-400' : 'text-red-400'}`}>{data.portfolioChange}</div>}
      </KpiCard>

      <KpiCard
        label="Signal Accuracy"
        value={data.signalAccuracy ?? '—'}
        badge="AI"
        badgeColor="text-cyan-400 border-cyan-400/20 bg-cyan-400/10"
      >
        {data.signalTrend && <div className="font-mono text-xs text-cyan-400">{data.signalTrend}</div>}
      </KpiCard>

      <KpiCard
        label="Active Alerts"
        value={data.alertCount !== null ? String(data.alertCount) : '—'}
        badge={data.alertCount !== null && data.alertCount > 0 ? String(data.alertCount) : undefined}
        badgeColor={data.alertCount !== null && data.alertCount > 0 ? 'text-amber-400 border-amber-400/20' : undefined}
      >
        {data.criticalAlerts && <div className="font-mono text-xs text-red-400">● 1 critical</div>}
      </KpiCard>

      <KpiCard
        label="S&P 500"
        value={data.sp500 ?? '—'}
        subValue={data.vix ? `VIX ${data.vix}` : undefined}
        subColor="text-white/30"
        badge={data.sp500 ? 'OPEN' : undefined}
        badgeColor={data.sp500 ? 'text-green-400 border-green-400/20 bg-green-400/10' : undefined}
      />
    </div>
  );
}

function KpiCard({
  label, value, subValue, subColor = 'text-white/20', badge, badgeColor, children,
}: {
  label: string;
  value: string | React.ReactNode;
  subValue?: string | React.ReactNode;
  subColor?: string;
  badge?: string;
  badgeColor?: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="glass-panel flex-1 px-4 py-3">
      <div className="flex items-center justify-between">
        <span className="text-[0.6rem] uppercase tracking-wider text-white/30">{label}</span>
        {badge && (
          <span className={`rounded-full border px-2 py-0.5 text-[0.55rem] ${badgeColor || 'text-white/30 border-white/10'}`}>
            {badge}
          </span>
        )}
      </div>
      <div className="mt-0.5 font-mono text-xl text-[#f0f6fc]">{value}</div>
      {children}
      {subValue && !children && (
        <div className={`font-mono text-xs ${subColor}`}>{subValue}</div>
      )}
    </div>
  );
}
