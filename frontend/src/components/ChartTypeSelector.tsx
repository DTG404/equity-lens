'use client';

import React from 'react';

const TYPES = [
  { id: 'candlestick', label: 'C' },
  { id: 'line', label: 'L' },
  { id: 'area', label: 'A' },
  { id: 'bar', label: 'B' },
];

interface Props {
  active: string;
  onChange: (type: string) => void;
}

export default function ChartTypeSelector({ active, onChange }: Props) {
  return (
    <div className="flex gap-0.5">
      {TYPES.map(t => (
        <button key={t.id} onClick={() => onChange(t.id)}
          className={`px-1.5 py-0.5 text-[0.55rem] font-mono rounded transition-colors ${
            active === t.id ? 'bg-cyan-400/10 text-cyan-400' : 'text-white/30 hover:text-white/60'
          }`}>
          {t.label}
        </button>
      ))}
    </div>
  );
}
