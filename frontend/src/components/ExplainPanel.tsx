'use client';

import React, { useState } from 'react';

interface ExplainData {
  explanation: string;
  key_takeaways: string[];
  questions_to_ask: string[];
}

interface Props {
  symbol: string;
  apiBase: string;
}

export default function ExplainPanel({ symbol, apiBase }: Props) {
  const [data, setData] = useState<ExplainData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExplain = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/research/${symbol}/explain`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to generate explanation');
      const result: ExplainData = await res.json();
      setData(result);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-4">
      <button
        onClick={handleExplain}
        disabled={loading}
        className="px-4 py-2 rounded-lg bg-cyan-600/20 text-cyan-400 border border-cyan-600/30
                   hover:bg-cyan-600/30 transition-colors text-sm font-medium
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Generating...' : data ? 'Regenerate' : 'Explain this to me'}
      </button>

      {error && <p className="mt-3 text-red-400 text-sm">{error}</p>}

      {data && (
        <div className="mt-4 space-y-4 text-sm">
          <p className="text-gray-200 leading-relaxed">{data.explanation}</p>
          {data.key_takeaways.length > 0 && (
            <div>
              <h4 className="text-cyan-400 font-semibold mb-2">Key Takeaways</h4>
              <ul className="space-y-1">
                {data.key_takeaways.map((t, i) => (
                  <li key={i} className="text-gray-300 flex gap-2"><span className="text-cyan-400 shrink-0">→</span>{t}</li>
                ))}
              </ul>
            </div>
          )}
          {data.questions_to_ask.length > 0 && (
            <div>
              <h4 className="text-amber-400 font-semibold mb-2">Questions to Ask Yourself</h4>
              <ul className="space-y-1">
                {data.questions_to_ask.map((q, i) => (
                  <li key={i} className="text-gray-300 flex gap-2"><span className="text-amber-400 shrink-0">?</span>{q}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
