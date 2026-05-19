'use client';

import React, { useState } from 'react';

interface Condition {
  indicator: string;
  operator: string;
  value: string;
}

interface StrategyForm {
  name: string;
  tickers: string;
  entry_conditions: Condition[];
  exit_conditions: Condition[];
}

interface Props {
  onRun: (strategy: object) => void;
  loading: boolean;
}

const INDICATORS = ['rsi', 'sma_20', 'sma_50', 'ema_12', 'ema_26'];
const OPERATORS = ['<', '>', '=='];

export default function BacktestBuilder({ onRun, loading }: Props) {
  const [form, setForm] = useState<StrategyForm>({
    name: '',
    tickers: 'AAPL,MSFT',
    entry_conditions: [{ indicator: 'rsi', operator: '<', value: '30' }],
    exit_conditions: [{ indicator: 'rsi', operator: '>', value: '70' }],
  });

  const addCondition = (type: 'entry' | 'exit') => {
    const key = type === 'entry' ? 'entry_conditions' : 'exit_conditions';
    setForm({ ...form, [key]: [...form[key], { indicator: 'rsi', operator: '>', value: '50' }] });
  };

  const updateCondition = (type: 'entry' | 'exit', index: number, field: keyof Condition, value: string) => {
    const key = type === 'entry' ? 'entry_conditions' : 'exit_conditions';
    const updated = [...form[key]];
    updated[index] = { ...updated[index], [field]: value };
    setForm({ ...form, [key]: updated });
  };

  const removeCondition = (type: 'entry' | 'exit', index: number) => {
    const key = type === 'entry' ? 'entry_conditions' : 'exit_conditions';
    setForm({ ...form, [key]: form[key].filter((_, i) => i !== index) });
  };

  const handleRun = () => {
    onRun({
      name: form.name || 'Backtest',
      tickers: form.tickers.split(',').map(t => t.trim().toUpperCase()).filter(Boolean),
      entry_conditions: form.entry_conditions,
      exit_conditions: form.exit_conditions,
    });
  };

  return (
    <div className="glass-panel p-4 space-y-4">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-white/40">Strategy Builder</h2>
      
      <div>
        <label className="text-[0.6rem] uppercase text-white/30 block mb-1">Name</label>
        <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
          className="w-full bg-white/5 border border-white/10 rounded px-2 py-1.5 text-xs text-white/70 font-mono outline-none focus:border-cyan-500/50" placeholder="RSI Oversold Bounce" />
      </div>

      <div>
        <label className="text-[0.6rem] uppercase text-white/30 block mb-1">Tickers (comma-separated)</label>
        <input value={form.tickers} onChange={e => setForm({ ...form, tickers: e.target.value })}
          className="w-full bg-white/5 border border-white/10 rounded px-2 py-1.5 text-xs text-white/70 font-mono outline-none focus:border-cyan-500/50" />
      </div>

      {(['entry', 'exit'] as const).map(type => (
        <div key={type}>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[0.6rem] uppercase text-white/30">{type} Conditions</label>
            <button onClick={() => addCondition(type)} className="text-[0.55rem] text-cyan-400 hover:text-cyan-300">+ Add</button>
          </div>
          {form[`${type}_conditions`].map((cond, i) => (
            <div key={i} className="flex gap-1 mb-1">
              <select value={cond.indicator} onChange={e => updateCondition(type, i, 'indicator', e.target.value)}
                className="bg-white/5 border border-white/10 rounded px-1 py-1 text-[0.6rem] text-white/60 font-mono outline-none focus:border-cyan-500/50">
                {INDICATORS.map(ind => <option key={ind} value={ind}>{ind.toUpperCase()}</option>)}
              </select>
              <select value={cond.operator} onChange={e => updateCondition(type, i, 'operator', e.target.value)}
                className="bg-white/5 border border-white/10 rounded px-1 py-1 text-[0.6rem] text-white/60 font-mono outline-none focus:border-cyan-500/50">
                {OPERATORS.map(op => <option key={op} value={op}>{op}</option>)}
              </select>
              <input value={cond.value} onChange={e => updateCondition(type, i, 'value', e.target.value)}
                className="w-16 bg-white/5 border border-white/10 rounded px-1 py-1 text-[0.6rem] text-white/70 font-mono outline-none focus:border-cyan-500/50" />
              <button onClick={() => removeCondition(type, i)} className="text-red-400 text-[0.55rem] px-1">✕</button>
            </div>
          ))}
        </div>
      ))}

      <button onClick={handleRun} disabled={loading}
        className="w-full py-2 rounded-lg bg-cyan-600/20 text-cyan-400 border border-cyan-600/30 hover:bg-cyan-600/30 transition-colors text-sm font-medium disabled:opacity-50">
        {loading ? 'Running...' : 'Run Backtest'}
      </button>
    </div>
  );
}
