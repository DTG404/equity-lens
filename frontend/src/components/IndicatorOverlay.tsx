'use client';

import React from 'react';

const INDICATORS = [
  { id: 'sma_20', label: 'SMA 20' },
  { id: 'sma_50', label: 'SMA 50' },
  { id: 'sma_200', label: 'SMA 200' },
  { id: 'ema_12', label: 'EMA 12' },
  { id: 'ema_26', label: 'EMA 26' },
  { id: 'bollinger', label: 'Bollinger' },
];

interface Props {
  visible: Record<string, boolean>;
  onToggle: (id: string) => void;
}

export default function IndicatorOverlay({ visible, onToggle }: Props) {
  return (
    <div className="flex flex-wrap gap-1">
      {INDICATORS.map(ind => (
        <button key={ind.id} onClick={() => onToggle(ind.id)}
          className={`px-1.5 py-0.5 text-[0.55rem] font-mono rounded transition-colors border ${
            visible[ind.id] ? 'bg-cyan-400/10 text-cyan-400 border-cyan-400/30' : 'text-white/30 border-white/10 hover:text-white/60'
          }`}>
          {ind.label}
        </button>
      ))}
    </div>
  );
}
