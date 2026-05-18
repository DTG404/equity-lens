'use client';

import React, { useEffect, useState } from 'react';
import { fetchMacro, type MacroData } from '@/lib/api';

function IndicatorCard({ indicator }: { indicator: { name: string; value: number; change: number | null; unit: string } }) {
  const changeColor = indicator.change === null ? 'text-white/30' : indicator.change >= 0 ? 'text-green-400' : 'text-red-400';
  const changeSign = indicator.change === null ? '' : indicator.change >= 0 ? '+' : '';

  return (
    <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
      <div className="text-[0.6rem] uppercase tracking-wider text-white/30">{indicator.name}</div>
      <div className="mt-0.5 font-mono text-lg font-bold text-[#f0f6fc]">
        {indicator.value}{indicator.unit}
      </div>
      {indicator.change !== null && (
        <div className={`font-mono text-xs ${changeColor}`}>
          {changeSign}{indicator.change}{indicator.unit}
        </div>
      )}
    </div>
  );
}

export default function MacroPanel() {
  const [data, setData] = useState<MacroData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMacro()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="glass-panel p-4">
        <p className="text-xs text-red-400">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="glass-panel p-4">
        <div className="flex animate-pulse gap-3">
          <div className="h-16 flex-1 rounded-lg bg-white/[0.03]" />
          <div className="h-16 flex-1 rounded-lg bg-white/[0.03]" />
          <div className="h-16 flex-1 rounded-lg bg-white/[0.03]" />
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-white/40">
          Macro Dashboard
        </h2>
        {data.note && (
          <span className="text-[0.55rem] text-amber-400/60">{data.note}</span>
        )}
      </div>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
        {data.indicators && Object.entries(data.indicators).map(([key, ind]) => (
          <IndicatorCard key={key} indicator={ind} />
        ))}
      </div>
    </div>
  );
}
