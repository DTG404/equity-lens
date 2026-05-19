'use client';

import React from 'react';
import type { SectorAllocation } from '@/lib/api';

const SECTOR_COLORS: Record<string, string> = {
  Technology: '#4ade80',
  Healthcare: '#60a5fa',
  Financials: '#f59e0b',
  'Consumer Cyclical': '#f472b6',
  Communication: '#a78bfa',
  Industrials: '#fb923c',
  'Consumer Defensive': '#34d399',
  Energy: '#f87171',
  'Basic Materials': '#fbbf24',
  'Real Estate': '#2dd4bf',
  Utilities: '#38bdf8',
  Unknown: '#6b7280',
};

function getSectorColor(sector: string): string {
  return SECTOR_COLORS[sector] ?? SECTOR_COLORS.Unknown;
}

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const angleRad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(angleRad),
    y: cy + r * Math.sin(angleRad),
  };
}

function describeArc(
  cx: number,
  cy: number,
  r: number,
  innerR: number,
  startAngle: number,
  endAngle: number,
) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const startInner = polarToCartesian(cx, cy, innerR, endAngle);
  const endInner = polarToCartesian(cx, cy, innerR, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';

  return [
    `M ${start.x} ${start.y}`,
    `A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`,
    `L ${endInner.x} ${endInner.y}`,
    `A ${innerR} ${innerR} 0 ${largeArcFlag} 1 ${startInner.x} ${startInner.y}`,
    'Z',
  ].join(' ');
}

interface AllocationChartProps {
  sectors: SectorAllocation[];
  totalValue: number;
}

export default function AllocationChart({ sectors, totalValue }: AllocationChartProps) {
  if (sectors.length === 0) {
    return (
      <div className="glass-panel flex h-[320px] items-center justify-center">
        <span className="text-sm text-white/30">No holdings to allocate</span>
      </div>
    );
  }

  const cx = 100;
  const cy = 100;
  const r = 80;
  const innerR = 52;

  let currentAngle = 0;
  const slices = sectors.map((sector) => {
    const sweep = sector.pct * 3.6;
    const startAngle = currentAngle;
    const endAngle = currentAngle + sweep;
    currentAngle = endAngle;
    return {
      ...sector,
      startAngle,
      endAngle,
      color: getSectorColor(sector.sector),
    };
  });

  return (
    <div className="glass-panel p-4">
      <div className="mb-3 border-b border-white/[0.04] pb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-white/40">
          Sector Allocation
        </span>
      </div>
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-center sm:justify-center">
        <div className="relative">
          <svg width={200} height={200} viewBox="0 0 200 200" className="block">
            {slices.map((slice, i) => (
              <path
                key={i}
                d={describeArc(cx, cy, r, innerR, slice.startAngle, slice.endAngle)}
                fill={slice.color}
                stroke="rgba(255,255,255,0.04)"
                strokeWidth={1}
              />
            ))}
            <text
              x={cx}
              y={cy - 6}
              textAnchor="middle"
              className="fill-[#f0f6fc]"
              style={{ fontSize: 13, fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" }}
            >
              ${totalValue.toLocaleString()}
            </text>
            <text
              x={cx}
              y={cy + 10}
              textAnchor="middle"
              className="fill-white/30"
              style={{ fontSize: 9, fontWeight: 500 }}
            >
              Total Value
            </text>
          </svg>
        </div>
        <div className="flex flex-col gap-1.5">
          {slices.map((slice, i) => (
            <div key={i} className="flex items-center gap-2">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: slice.color }}
              />
              <span className="text-[0.65rem] text-white/50">{slice.sector}</span>
              <span className="ml-auto font-mono text-[0.65rem] text-white/40">
                {slice.pct.toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
