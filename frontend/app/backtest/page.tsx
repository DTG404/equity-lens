'use client';

import React, { useState } from 'react';
import BacktestBuilder from '@/components/BacktestBuilder';
import BacktestResults from '@/components/BacktestResults';
import { runBacktest, BacktestResult } from '@/lib/api';
import NavBar from '@/components/NavBar';
import StatusBar from '@/components/StatusBar';

export default function BacktestPage() {
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async (strategy: object) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await runBacktest(strategy);
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col">
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />
      <NavBar />
      <main className="relative z-10 mx-3 my-3 flex-1">
        <h1 className="text-lg font-semibold text-gray-200 mb-4">Backtest</h1>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <BacktestBuilder onRun={handleRun} loading={loading} />
          </div>
          <div className="lg:col-span-2">
            {error && <div className="glass-panel p-4"><p className="text-xs text-red-400">{error}</p></div>}
            {result && <BacktestResults result={result} />}
            {!result && !error && (
              <div className="glass-panel p-4 text-center">
                <p className="text-xs text-white/30">Configure your strategy and click &quot;Run Backtest&quot; to see results.</p>
              </div>
            )}
          </div>
        </div>
      </main>
      <StatusBar />
    </div>
  );
}
