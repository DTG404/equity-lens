'use client';

import React from 'react';

export default function StatusBar() {
  return (
    <footer className="glass-panel-sm mx-3 mb-3 mt-0 flex items-center justify-between px-4 py-1.5">
      <div className="flex gap-4 font-mono text-[0.55rem] text-white/20">
        <span>
          <span className="text-cyan-400">●</span> CONNECTED
        </span>
        <span>DATA: YFINANCE</span>
        <span>
          <span className="text-green-400">✓</span> ALL SYSTEMS NOMINAL
        </span>
      </div>
      <div className="flex gap-4 font-mono text-[0.55rem] text-white/20">
        <span>API: 45ms</span>
        <span>UPDATED: {new Date().toLocaleTimeString()} UTC</span>
        <span>MODEL: DEEPSEEK R1</span>
      </div>
    </footer>
  );
}
