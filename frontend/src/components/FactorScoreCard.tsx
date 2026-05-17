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

const factorLabels: Record<FactorKey, string> = {
  technical: 'Technical',
  news_sentiment: 'News Sentiment',
  fundamentals: 'Fundamentals',
  macro: 'Macro',
};

function ScoreBar({
  label,
  score,
  explanation,
}: {
  label: string;
  score: number;
  explanation: string;
}) {
  const [hovered, setHovered] = useState(false);
  const percentage = Math.round(score * 100);

  const barColor =
    score >= 0.7 ? '#22c55e' : score >= 0.4 ? '#eab308' : '#ef4444';

  return (
    <div
      style={{ marginBottom: 16, position: 'relative' }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 6,
        }}
      >
        <span style={{ fontSize: 14, fontWeight: 600 }}>{label}</span>
        <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          {percentage}%
        </span>
      </div>
      <div
        style={{
          width: '100%',
          height: 8,
          background: 'var(--bg-secondary)',
          borderRadius: 4,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${percentage}%`,
            height: '100%',
            background: barColor,
            borderRadius: 4,
            transition: 'width 0.3s ease',
          }}
        />
      </div>
      {hovered && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            marginTop: 4,
            padding: '8px 12px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 6,
            fontSize: 12,
            color: 'var(--text-secondary)',
            zIndex: 10,
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          }}
        >
          {explanation}
        </div>
      )}
    </div>
  );
}

export default function FactorScoreCard({ scores }: FactorScoreCardProps) {
  const overallPercentage = Math.round(scores.overall * 100);

  const overallColor =
    scores.overall >= 0.7
      ? '#22c55e'
      : scores.overall >= 0.4
        ? '#eab308'
        : '#ef4444';

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        borderRadius: 8,
        padding: 20,
        border: '1px solid var(--border)',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 20,
          paddingBottom: 16,
          borderBottom: '1px solid var(--border)',
        }}
      >
        <span style={{ fontSize: 16, fontWeight: 700 }}>Factor Scores</span>
        <div style={{ textAlign: 'right' }}>
          <div
            style={{
              fontSize: 24,
              fontWeight: 800,
              color: overallColor,
              lineHeight: 1,
            }}
          >
            {overallPercentage}%
          </div>
          <div
            style={{
              fontSize: 11,
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: 0.5,
              marginTop: 2,
            }}
          >
            Overall
          </div>
        </div>
      </div>

      {(Object.keys(factorLabels) as FactorKey[]).map((key) => (
        <ScoreBar
          key={key}
          label={factorLabels[key]}
          score={scores[key].score}
          explanation={scores[key].explanation}
        />
      ))}
    </div>
  );
}
