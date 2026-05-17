import React from 'react';

export interface ScenarioCardProps {
  bullCase: string;
  baseCase: string;
  bearCase: string;
}

export default function ScenarioCard({ bullCase, baseCase, bearCase }: ScenarioCardProps) {
  const scenarios = [
    {
      title: 'Bull Case',
      text: bullCase,
      headerColor: '#22c55e',
      borderColor: 'rgba(34, 197, 94, 0.3)',
    },
    {
      title: 'Base Case',
      text: baseCase,
      headerColor: '#3b82f6',
      borderColor: 'rgba(59, 130, 246, 0.3)',
    },
    {
      title: 'Bear Case',
      text: bearCase,
      headerColor: '#ef4444',
      borderColor: 'rgba(239, 68, 68, 0.3)',
    },
  ];

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: 16,
      }}
    >
      {scenarios.map((scenario) => (
        <div
          key={scenario.title}
          style={{
            background: 'var(--bg-card)',
            borderRadius: 8,
            border: `1px solid ${scenario.borderColor}`,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              background: scenario.headerColor,
              color: '#fff',
              fontSize: 14,
              fontWeight: 700,
              padding: '10px 14px',
              textAlign: 'center',
            }}
          >
            {scenario.title}
          </div>
          <div
            style={{
              padding: 14,
              fontSize: 13,
              lineHeight: 1.6,
              color: 'var(--text-primary)',
            }}
          >
            {scenario.text}
          </div>
        </div>
      ))}
    </div>
  );
}
