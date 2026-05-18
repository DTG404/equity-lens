'use client';

import React from 'react';

interface KpiCardProps {
  label: string;
  value: string | React.ReactNode;
  subValue?: string | React.ReactNode;
  subColor?: string;
  badge?: string;
  badgeColor?: string;
  children?: React.ReactNode;
}

function KpiCard({ label, value, subValue, subColor = 'text-white/20', badge, badgeColor, children }: KpiCardProps) {
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
      {subValue && (
        <div className={`font-mono text-xs ${subColor}`}>{subValue}</div>
      )}
      {children}
    </div>
  );
}

export default function KpiStrip() {
  return (
    <div className="mx-3 mt-2 flex gap-2">
      <KpiCard
        label="Portfolio Value"
        value="$247,832"
        subValue="▲ +3.42% today"
        subColor="text-green-400"
      />
      <KpiCard
        label="Signal Accuracy"
        value="76.4%"
        subValue="↑ improving  +2.1% vs last month"
        subColor="text-cyan-400"
        badge="AI"
        badgeColor="text-cyan-400 border-cyan-400/20 bg-cyan-400/10"
      />
      <KpiCard
        label="Active Alerts"
        value="3"
        subValue="● 1 critical"
        subColor="text-red-400"
        badge="4"
        badgeColor="text-amber-400 border-amber-400/20"
      />
      <KpiCard
        label="Markets"
        value={
          <>
            S&P <span className="text-green-400">+0.8%</span>
          </>
        }
        subValue="VIX 14.2 ↓"
        subColor="text-white/30"
        badge="OPEN"
        badgeColor="text-green-400 border-green-400/20 bg-green-400/10"
      />
    </div>
  );
}
