'use client';

import React, { useEffect, useState } from 'react';
import { fetchMacro, fetchSectorPerformance, type MacroData, type SectorPerformanceData } from '@/lib/api';

type Tab = 'macro' | 'sectors';

const PERIODS = ['1d', '1w', '1m', '1y'] as const;

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

function SectorTable({ data }: { data: SectorPerformanceData }) {
  return (
    <div className="space-y-1">
      {data.sectors.map((sector, i) => {
        const color = sector.return_pct >= 0 ? 'text-green-400' : 'text-red-400';
        const sign = sector.return_pct >= 0 ? '+' : '';
        return (
          <div
            key={sector.name}
            className="flex items-center justify-between rounded-md border border-white/[0.06] bg-white/[0.02] px-3 py-2"
          >
            <div className="flex items-center gap-3">
              <span className="w-4 text-[0.6rem] text-white/20">{i + 1}</span>
              <span className="text-xs text-[#f0f6fc]">{sector.name}</span>
            </div>
            <div className="flex items-center gap-3 font-mono text-xs">
              <span className={color}>
                {sign}{sector.return_pct}%
              </span>
              <span className="text-white/30">{sector.constituent_count}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function MacroPanel() {
  const [tab, setTab] = useState<Tab>('macro');
  const [macroData, setMacroData] = useState<MacroData | null>(null);
  const [sectorData, setSectorData] = useState<SectorPerformanceData | null>(null);
  const [sectorPeriod, setSectorPeriod] = useState<string>('1d');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (tab === 'macro') {
      setError(null);
      fetchMacro()
        .then(setMacroData)
        .catch((err) => setError(err.message));
    }
  }, [tab]);

  useEffect(() => {
    if (tab === 'sectors') {
      setError(null);
      fetchSectorPerformance(sectorPeriod)
        .then(setSectorData)
        .catch((err) => setError(err.message));
    }
  }, [tab, sectorPeriod]);

  if (error) {
    return (
      <div className="glass-panel p-4">
        <p className="text-xs text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex gap-1 rounded-lg border border-white/[0.06] bg-white/[0.03] p-0.5">
          <button
            onClick={() => setTab('macro')}
            className={`rounded-md px-2.5 py-1 text-[0.6rem] font-semibold uppercase tracking-wider transition-colors ${
              tab === 'macro'
                ? 'bg-white/[0.08] text-[#f0f6fc]'
                : 'text-white/40 hover:text-white/60'
            }`}
          >
            Macro
          </button>
          <button
            onClick={() => setTab('sectors')}
            className={`rounded-md px-2.5 py-1 text-[0.6rem] font-semibold uppercase tracking-wider transition-colors ${
              tab === 'sectors'
                ? 'bg-white/[0.08] text-[#f0f6fc]'
                : 'text-white/40 hover:text-white/60'
            }`}
          >
            Sectors
          </button>
        </div>
        {tab === 'macro' && macroData?.note && (
          <span className="text-[0.55rem] text-amber-400/60">{macroData.note}</span>
        )}
        {tab === 'sectors' && (
          <div className="flex gap-1 rounded-lg border border-white/[0.06] bg-white/[0.03] p-0.5">
            {PERIODS.map((p) => (
              <button
                key={p}
                onClick={() => setSectorPeriod(p)}
                className={`rounded-md px-2 py-0.5 text-[0.55rem] font-semibold uppercase tracking-wider transition-colors ${
                  sectorPeriod === p
                    ? 'bg-white/[0.08] text-[#f0f6fc]'
                    : 'text-white/30 hover:text-white/60'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        )}
      </div>

      {tab === 'macro' && !macroData && (
        <div className="flex animate-pulse gap-3">
          <div className="h-16 flex-1 rounded-lg bg-white/[0.03]" />
          <div className="h-16 flex-1 rounded-lg bg-white/[0.03]" />
          <div className="h-16 flex-1 rounded-lg bg-white/[0.03]" />
        </div>
      )}

      {tab === 'macro' && macroData && (
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
          {macroData.indicators && Object.entries(macroData.indicators).map(([key, ind]) => (
            <IndicatorCard key={key} indicator={ind} />
          ))}
        </div>
      )}

      {tab === 'sectors' && !sectorData && (
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-8 animate-pulse rounded-md bg-white/[0.03]" />
          ))}
        </div>
      )}

      {tab === 'sectors' && sectorData && <SectorTable data={sectorData} />}
    </div>
  );
}
