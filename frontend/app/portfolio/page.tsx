'use client';

import React from 'react';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';

export default function PortfolioPage() {
  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />

      <main className="relative z-10 mx-3 my-3 flex flex-1 items-center justify-center">
        <div className="glass-panel w-full max-w-lg p-8 text-center">
          <div className="mb-4 text-4xl">💼</div>
          <h1 className="mb-2 text-lg font-semibold text-[#f0f6fc]">Portfolio</h1>
          <p className="mb-6 text-sm text-white/40">
            Track your holdings, monitor P&amp;L, and compare performance against benchmarks.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="text-xs text-white/30">Portfolio Value</div>
              <div className="font-mono text-lg font-bold text-[#f0f6fc]">$247.8k</div>
            </div>
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="text-xs text-white/30">Total Return</div>
              <div className="font-mono text-lg font-bold text-green-400">+12.4%</div>
            </div>
          </div>
          <div className="mt-4 rounded-lg border border-cyan-400/10 bg-cyan-400/5 p-3 text-xs text-cyan-400/60">
            Connect a brokerage or import a CSV to see your real portfolio
          </div>
          <p className="mt-6 text-xs text-white/20">
            Broker sync, P&L tracking, benchmark comparison, and allocation charts coming soon
          </p>
        </div>
      </main>

      <StatusBar />
    </div>
  );
}
