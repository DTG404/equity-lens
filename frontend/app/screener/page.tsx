'use client';

import React from 'react';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';

export default function ScreenerPage() {
  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />

      <main className="relative z-10 mx-3 my-3 flex flex-1 items-center justify-center">
        <div className="glass-panel w-full max-w-lg p-8 text-center">
          <div className="mb-4 text-4xl">⚡</div>
          <h1 className="mb-2 text-lg font-semibold text-[#f0f6fc]">Stock Screener</h1>
          <p className="mb-4 text-sm text-white/40">
            Filter the market by price, sector, fundamentals, and technical signals.
          </p>
          <div className="flex flex-wrap justify-center gap-2 text-xs">
            <span className="glass-badge-cyan rounded-lg px-3 py-1.5">Price</span>
            <span className="rounded-lg border border-white/[0.06] px-3 py-1.5 text-white/40">Market Cap</span>
            <span className="rounded-lg border border-white/[0.06] px-3 py-1.5 text-white/40">Sector</span>
            <span className="rounded-lg border border-white/[0.06] px-3 py-1.5 text-white/40">P/E</span>
            <span className="rounded-lg border border-white/[0.06] px-3 py-1.5 text-white/40">RSI</span>
            <span className="rounded-lg border border-white/[0.06] px-3 py-1.5 text-white/40">Volume</span>
          </div>
          <p className="mt-6 text-xs text-white/20">
            Coming soon — SEC EDGAR fundamentals + TA-Lib technicals + AI scoring
          </p>
        </div>
      </main>

      <StatusBar />
    </div>
  );
}
