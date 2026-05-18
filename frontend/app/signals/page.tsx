'use client';

import React from 'react';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';

export default function SignalsPage() {
  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />

      <main className="relative z-10 mx-3 my-3 flex flex-1 items-center justify-center">
        <div className="glass-panel w-full max-w-lg p-8 text-center">
          <div className="mb-4 text-4xl">📊</div>
          <h1 className="mb-2 text-lg font-semibold text-[#f0f6fc]">Signal History</h1>
          <p className="mb-6 text-sm text-white/40">
            Track AI signal accuracy, view historical outcomes, and analyze performance by stance and timeframe.
          </p>
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="text-xs text-white/30">Accuracy</div>
              <div className="font-mono text-lg font-bold text-green-400">76.4%</div>
            </div>
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="text-xs text-white/30">Signals</div>
              <div className="font-mono text-lg font-bold text-[#f0f6fc]">247</div>
            </div>
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="text-xs text-white/30">Avg Return</div>
              <div className="font-mono text-lg font-bold text-cyan-400">+3.2%</div>
            </div>
          </div>
          <p className="mt-6 text-xs text-white/20">
            Full signal dashboard with filtering, charting, and export coming soon
          </p>
        </div>
      </main>

      <StatusBar />
    </div>
  );
}
