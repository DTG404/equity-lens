'use client';

import React, { useState } from 'react';

export interface FactorScore {
  score: number;
  explanation: string;
}

interface FactorScoreCardProps {
  scores: {
    technical: FactorScore;
    news_sentiment: FactorScore;
    fundamentals: FactorScore;
    macro: FactorScore;
    overall: number;
  };
}

type FactorKey = 'technical' | 'news_sentiment' | 'fundamentals' | 'macro';

const factorConfig: Record<FactorKey, { label: string; gradient: string }> = {
  technical: { label: 'Technical', gradient: 'from-green-400 to-cyan-400' },
  news_sentiment: { label: 'News Sentiment', gradient: 'from-amber-400 to-orange-400' },
  fundamentals: { label: 'Fundamentals', gradient: 'from-cyan-400 to-blue-400' },
  macro: { label: 'Macro', gradient: 'from-purple-400 to-pink-400' },
};

function ScoreBar({ label, score, explanation, gradient }: { label: string; score: number; explanation: string; gradient: string }) {
  const [hovered, setHovered] = useState(false);
  const percentage = Math.round(score * 100);

  const barColor =
    score >= 0.7 ? 'bg-green-400' : score >= 0.4 ? 'bg-amber-400' : 'bg-red-400';

  return (
    <div
      className="relative mb-3"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs font-semibold text-white/60">{label}</span>
        <span className="font-mono text-xs text-white/40">{percentage}%</span>
      </div>
      <div className={`h-2 w-full overflow-hidden rounded-full bg-white/[0.04]`}>
        <div
          className={`h-full rounded-full bg-gradient-to-r ${gradient} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {hovered && (
        <div className="glass-panel-sm absolute left-0 right-0 top-full z-10 mt-1 px-3 py-2 text-xs text-white/50 shadow-lg">
          {explanation}
        </div>
      )}
    </div>
  );
}

export default function FactorScoreCard({ scores }: FactorScoreCardProps) {
  const overallPercentage = Math.round(scores.overall * 100);
  const overallColor =
    scores.overall >= 0.7 ? 'text-green-400' : scores.overall >= 0.4 ? 'text-amber-400' : 'text-red-400';

  return (
    <div className="glass-panel p-4">
      <div className="mb-4 flex items-center justify-between border-b border-white/[0.04] pb-4">
        <span className="text-xs font-semibold uppercase tracking-wider text-white/40">
          Factor Scores
        </span>
        <div className="text-right">
          <div className={`font-mono text-2xl font-bold leading-none ${overallColor}`}>
            {overallPercentage}%
          </div>
          <div className="mt-0.5 text-[0.6rem] uppercase tracking-wider text-white/30">
            Overall
          </div>
        </div>
      </div>

      {(Object.keys(factorConfig) as FactorKey[]).map((key) => (
        <ScoreBar
          key={key}
          label={factorConfig[key].label}
          score={scores[key].score}
          explanation={scores[key].explanation}
          gradient={factorConfig[key].gradient}
        />
      ))}
    </div>
  );
}
