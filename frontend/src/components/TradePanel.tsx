'use client';

import React, { useState } from 'react';
import { placeOrder, OrderResult } from '@/lib/api';

interface Props {
  symbol: string;
  currentPrice: number;
}

const QTY_PRESETS = [1, 5, 10, 25, 50, 100];

export default function TradePanel({ symbol, currentPrice }: Props) {
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [qty, setQty] = useState(10);
  const [orderType] = useState('market');
  const [confirming, setConfirming] = useState(false);
  const [result, setResult] = useState<OrderResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await placeOrder({ symbol, side, quantity: qty, order_type: orderType });
      setResult(res);
      setConfirming(false);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Order failed');
    } finally {
      setLoading(false);
    }
  };

  const estimatedCost = qty * currentPrice;

  return (
    <div className="glass-panel p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-3">Trade</h3>

      {result ? (
        <div className="text-center">
          <div className={`text-lg font-bold font-mono mb-1 ${result.status === 'filled' ? 'text-green-400' : result.status === 'rejected' ? 'text-red-400' : 'text-amber-400'}`}>
            {result.status === 'filled' ? '\u2713 Filled' : result.status === 'rejected' ? '\u2717 Rejected' : '\u25c7 Pending'}
          </div>
          <div className="text-xs text-white/50">
            {result.side.toUpperCase()} {result.filled_qty || qty} {result.symbol}
            {result.filled_price > 0 && ` @ $${result.filled_price.toFixed(2)}`}
          </div>
          <button onClick={() => { setResult(null); setQty(10); }} className="mt-3 text-[0.55rem] text-cyan-400 hover:text-cyan-300">
            New Order
          </button>
        </div>
      ) : confirming ? (
        <div className="text-center">
          <p className="text-xs text-white/70 mb-2">
            {side === 'buy' ? 'Buy' : 'Sell'} <span className="font-bold text-white/90">{qty}</span> shares of <span className="font-bold text-white/90">{symbol}</span>
          </p>
          <p className="text-xs text-white/50 mb-3">Est. {estimatedCost.toLocaleString('en-US', {style:'currency', currency:'USD'})}</p>
          <div className="flex gap-2 justify-center">
            <button onClick={handleSubmit} disabled={loading}
              className={`px-4 py-1.5 rounded text-xs font-medium ${side === 'buy' ? 'bg-green-600/20 text-green-400 border border-green-600/30' : 'bg-red-600/20 text-red-400 border border-red-600/30'} hover:opacity-80 disabled:opacity-50`}>
              {loading ? 'Sending...' : 'Confirm'}
            </button>
            <button onClick={() => setConfirming(false)} className="px-4 py-1.5 rounded text-xs text-white/40 border border-white/10 hover:text-white/60">
              Cancel
            </button>
          </div>
          {error && <p className="text-xs text-red-400 mt-2">{error}</p>}
        </div>
      ) : (
        <>
          <div className="flex gap-1 mb-3">
            <button onClick={() => setSide('buy')}
              className={`flex-1 py-1.5 rounded text-xs font-medium ${side === 'buy' ? 'bg-green-600/20 text-green-400 border border-green-600/30' : 'text-white/40 border border-white/10'}`}>
              Buy
            </button>
            <button onClick={() => setSide('sell')}
              className={`flex-1 py-1.5 rounded text-xs font-medium ${side === 'sell' ? 'bg-red-600/20 text-red-400 border border-red-600/30' : 'text-white/40 border border-white/10'}`}>
              Sell
            </button>
          </div>

          <div className="mb-3">
            <label className="text-[0.55rem] uppercase text-white/30 block mb-1">Quantity</label>
            <input type="number" value={qty} onChange={e => setQty(parseInt(e.target.value) || 0)}
              className="w-full bg-white/5 border border-white/10 rounded px-2 py-1.5 text-xs text-white/70 font-mono outline-none focus:border-cyan-500/50" min={1} />
            <div className="flex gap-1 mt-1">
              {QTY_PRESETS.map(p => (
                <button key={p} onClick={() => setQty(p)}
                  className={`flex-1 py-0.5 rounded text-[0.5rem] font-mono ${qty === p ? 'bg-cyan-400/10 text-cyan-400' : 'text-white/30 hover:text-white/50'}`}>
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="text-[0.55rem] text-white/30 mb-3">
            Est. {estimatedCost.toLocaleString('en-US', {style:'currency', currency:'USD'})} @ ${currentPrice.toFixed(2)}/share
          </div>

          <button onClick={() => setConfirming(true)} disabled={qty <= 0}
            className={`w-full py-2 rounded text-xs font-medium disabled:opacity-50 ${
              side === 'buy'
                ? 'bg-green-600/20 text-green-400 border border-green-600/30 hover:bg-green-600/30'
                : 'bg-red-600/20 text-red-400 border border-red-600/30 hover:bg-red-600/30'
            }`}>
            {side === 'buy' ? `Buy ${qty} ${symbol}` : `Sell ${qty} ${symbol}`}
          </button>
        </>
      )}
    </div>
  );
}
