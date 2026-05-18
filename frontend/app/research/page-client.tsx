'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';

export default function ResearchPage() {
  const [symbol, setSymbol] = useState('');
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (symbol.trim()) {
      router.push(`/stocks/${symbol.trim().toUpperCase()}`);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />

      <main className="relative z-10 mx-3 my-3 flex flex-1 items-center justify-center">
        <div className="glass-panel w-full max-w-lg p-8 text-center">
          <div className="mb-4 text-4xl">🔍</div>
          <h1 className="mb-2 text-lg font-semibold text-[#f0f6fc]">Research a Stock</h1>
          <p className="mb-6 text-sm text-white/40">
            Enter a ticker symbol to view AI-powered analysis
          </p>

          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              placeholder="Ticker symbol (e.g. AAPL)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="flex-1 rounded-lg border border-white/[0.06] bg-white/[0.03] px-4 py-3 text-center font-mono text-lg text-[#f0f6fc] uppercase placeholder-white/25 outline-none transition-colors focus:border-cyan-400/30"
              autoFocus
            />
            <button
              type="submit"
              className="glass-badge-cyan rounded-lg px-6 py-3 text-sm font-semibold uppercase tracking-wider transition-opacity hover:opacity-80"
            >
              Go
            </button>
          </form>

          <div className="mt-6 flex justify-center gap-2 text-xs text-white/25">
            <span className="rounded-md border border-white/[0.06] px-2 py-1 font-mono">⌘K</span>
            <span className="text-white/15">or type a symbol above</span>
          </div>
        </div>
      </main>

      <StatusBar />
    </div>
  );
}
