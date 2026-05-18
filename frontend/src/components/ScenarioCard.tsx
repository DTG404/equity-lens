import React from 'react';

export interface ScenarioCardProps {
  bullCase: string;
  baseCase: string;
  bearCase: string;
}

const scenarios = [
  { key: 'bull', title: 'Bull Case', borderColor: 'border-green-500/20', bgColor: 'bg-green-500/5', dotColor: 'bg-green-400' },
  { key: 'base', title: 'Base Case', borderColor: 'border-cyan-500/20', bgColor: 'bg-cyan-500/5', dotColor: 'bg-cyan-400' },
  { key: 'bear', title: 'Bear Case', borderColor: 'border-red-500/20', bgColor: 'bg-red-500/5', dotColor: 'bg-red-400' },
];

export default function ScenarioCard({ bullCase, baseCase, bearCase }: ScenarioCardProps) {
  const textMap = { bull: bullCase, base: baseCase, bear: bearCase };

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      {scenarios.map((s) => (
        <div key={s.key} className={`glass-panel overflow-hidden ${s.borderColor} ${s.bgColor}`}>
          <div className="flex items-center gap-2 border-b border-white/[0.04] px-3 py-2">
            <span className={`h-1.5 w-1.5 rounded-full ${s.dotColor}`} />
            <span className="text-xs font-bold uppercase tracking-wider text-white/60">
              {s.title}
            </span>
          </div>
          <div className="px-3 py-2 text-xs leading-relaxed text-white/50">
            {textMap[s.key as 'bull' | 'base' | 'bear']}
          </div>
        </div>
      ))}
    </div>
  );
}
