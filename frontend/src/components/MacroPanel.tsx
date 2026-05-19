'use client';

import React, { useEffect, useState, useMemo } from 'react';
import {
  fetchMacro,
  fetchMarketsOverview,
  fetchScreener,
  type MacroData,
  type MarketsOverview,
  type ScreenerResult,
} from '@/lib/api';

type TabKey = 'macro' | 'markets' | 'sectors' | 'global';

const TABS: { key: TabKey; label: string }[] = [
  { key: 'macro', label: 'Macro' },
  { key: 'markets', label: 'Markets' },
  { key: 'sectors', label: 'Sectors' },
  { key: 'global', label: 'Global' },
];

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

function IndexTable({ items }: { items: { symbol: string; name: string; price: number; change_pct: number }[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/[0.04] text-[0.6rem] font-medium uppercase tracking-wider text-white/30">
            <th className="py-2 text-left">Symbol</th>
            <th className="py-2 text-left">Name</th>
            <th className="py-2 text-right">Price</th>
            <th className="py-2 text-right">Change</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const changeColor = item.change_pct >= 0 ? 'text-green-400' : 'text-red-400';
            const changeSign = item.change_pct >= 0 ? '+' : '';
            return (
              <tr key={item.symbol} className="border-b border-white/[0.03] transition-colors hover:bg-white/[0.01]">
                <td className="py-2 font-mono font-semibold text-[#f0f6fc]">{item.symbol}</td>
                <td className="py-2 text-white/60">{item.name}</td>
                <td className="py-2 text-right font-mono text-[#f0f6fc]">${item.price.toFixed(2)}</td>
                <td className={`py-2 text-right font-mono ${changeColor}`}>
                  {changeSign}{item.change_pct.toFixed(2)}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function BreadthMetrics({ breadth }: { breadth: { advancers: number; decliners: number; advance_decline_ratio: number; new_highs: number; new_lows: number } }) {
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
      <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
        <div className="text-[0.6rem] uppercase tracking-wider text-white/30">Advancers</div>
        <div className="mt-0.5 font-mono text-lg font-bold text-green-400">{breadth.advancers}</div>
      </div>
      <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
        <div className="text-[0.6rem] uppercase tracking-wider text-white/30">Decliners</div>
        <div className="mt-0.5 font-mono text-lg font-bold text-red-400">{breadth.decliners}</div>
      </div>
      <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
        <div className="text-[0.6rem] uppercase tracking-wider text-white/30">A/D Ratio</div>
        <div className={`mt-0.5 font-mono text-lg font-bold ${breadth.advance_decline_ratio >= 1 ? 'text-green-400' : 'text-red-400'}`}>
          {breadth.advance_decline_ratio.toFixed(2)}
        </div>
      </div>
      <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
        <div className="text-[0.6rem] uppercase tracking-wider text-white/30">New Highs</div>
        <div className="mt-0.5 font-mono text-lg font-bold text-green-400">{breadth.new_highs}</div>
      </div>
      <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
        <div className="text-[0.6rem] uppercase tracking-wider text-white/30">New Lows</div>
        <div className="mt-0.5 font-mono text-lg font-bold text-red-400">{breadth.new_lows}</div>
      </div>
    </div>
  );
}

function SectorTable({ sectors }: { sectors: { sector: string; avgChange: number; count: number }[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/[0.04] text-[0.6rem] font-medium uppercase tracking-wider text-white/30">
            <th className="py-2 text-left">Sector</th>
            <th className="py-2 text-right">Tickers</th>
            <th className="py-2 text-right">Avg Change</th>
          </tr>
        </thead>
        <tbody>
          {sectors.map((s) => {
            const changeColor = s.avgChange >= 0 ? 'text-green-400' : 'text-red-400';
            const changeSign = s.avgChange >= 0 ? '+' : '';
            return (
              <tr key={s.sector} className="border-b border-white/[0.03] transition-colors hover:bg-white/[0.01]">
                <td className="py-2 font-semibold text-[#f0f6fc]">{s.sector}</td>
                <td className="py-2 text-right font-mono text-white/60">{s.count}</td>
                <td className={`py-2 text-right font-mono ${changeColor}`}>
                  {changeSign}{s.avgChange.toFixed(2)}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default function MacroPanel() {
  const [activeTab, setActiveTab] = useState<TabKey>('macro');
  const [macroData, setMacroData] = useState<MacroData | null>(null);
  const [marketData, setMarketData] = useState<MarketsOverview | null>(null);
  const [screenerData, setScreenerData] = useState<ScreenerResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMacro()
      .then(setMacroData)
      .catch((err) => setError(err.message));

    fetchMarketsOverview()
      .then(setMarketData)
      .catch((err) => setError(err.message));

    fetchScreener({ limit: 100 })
      .then((res) => setScreenerData(res.results))
      .catch((err) => setError(err.message));
  }, []);

  const sectorPerformance = useMemo(() => {
    const map = new Map<string, { totalChange: number; count: number }>();
    screenerData.forEach((item) => {
      if (!item.sector) return;
      const existing = map.get(item.sector);
      if (existing) {
        existing.totalChange += item.change_percent;
        existing.count += 1;
      } else {
        map.set(item.sector, { totalChange: item.change_percent, count: 1 });
      }
    });
    const arr = Array.from(map.entries()).map(([sector, data]) => ({
      sector,
      avgChange: data.totalChange / data.count,
      count: data.count,
    }));
    arr.sort((a, b) => b.avgChange - a.avgChange);
    return arr;
  }, [screenerData]);

  if (error) {
    return (
      <div className="glass-panel p-4">
        <p className="text-xs text-red-400">{error}</p>
      </div>
    );
  }

  const isLoading = activeTab === 'macro' && !macroData && !marketData;

  if (isLoading) {
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
      <div className="mb-3 flex items-center justify-between border-b border-white/[0.04] pb-2">
        <div className="flex gap-1">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`rounded-md px-3 py-1.5 text-[0.65rem] font-semibold uppercase tracking-wider transition-colors ${
                activeTab === tab.key
                  ? 'bg-white/[0.06] text-[#f0f6fc]'
                  : 'text-white/30 hover:bg-white/[0.03] hover:text-white/50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        {activeTab === 'macro' && macroData?.note && (
          <span className="text-[0.55rem] text-amber-400/60">{macroData.note}</span>
        )}
      </div>

      {activeTab === 'macro' && macroData && (
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
          {macroData.indicators && Object.entries(macroData.indicators).map(([key, ind]) => (
            <IndicatorCard key={key} indicator={ind} />
          ))}
        </div>
      )}

      {activeTab === 'markets' && marketData && (
        <div className="flex flex-col gap-3">
          {marketData.indices.length > 0 && (
            <div>
              <h3 className="mb-2 text-[0.65rem] font-semibold uppercase tracking-wider text-white/40">Indices</h3>
              <IndexTable items={marketData.indices} />
            </div>
          )}
          {marketData.breadth && (
            <div>
              <h3 className="mb-2 text-[0.65rem] font-semibold uppercase tracking-wider text-white/40">Market Breadth</h3>
              <BreadthMetrics breadth={marketData.breadth} />
            </div>
          )}
          {marketData.commodities.length > 0 && (
            <div>
              <h3 className="mb-2 text-[0.65rem] font-semibold uppercase tracking-wider text-white/40">Commodities</h3>
              <IndexTable items={marketData.commodities} />
            </div>
          )}
        </div>
      )}

      {activeTab === 'sectors' && (
        <div>
          <h3 className="mb-2 text-[0.65rem] font-semibold uppercase tracking-wider text-white/40">Sector Performance</h3>
          {sectorPerformance.length > 0 ? (
            <SectorTable sectors={sectorPerformance} />
          ) : (
            <div className="py-6 text-center text-xs text-white/25">No sector data available</div>
          )}
        </div>
      )}

      {activeTab === 'global' && marketData && (
        <div>
          <h3 className="mb-2 text-[0.65rem] font-semibold uppercase tracking-wider text-white/40">Global Indices</h3>
          {marketData.global.length > 0 ? (
            <IndexTable items={marketData.global} />
          ) : (
            <div className="py-6 text-center text-xs text-white/25">No global data available</div>
          )}
        </div>
      )}
    </div>
  );
}
