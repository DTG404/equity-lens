'use client';

import React, { useState } from 'react';
import { GLOSSARY, GlossaryEntry } from '@/lib/glossary';

interface Props {
  term: string;
  children: React.ReactNode;
}

export default function MetricTooltip({ term, children }: Props) {
  const [show, setShow] = useState(false);
  const entry: GlossaryEntry | undefined = GLOSSARY[term];

  if (!entry) return <>{children}</>;

  return (
    <span className="relative inline-flex items-center gap-1">
      <span
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onClick={() => setShow(!show)}
        className="border-b border-dashed border-gray-500 cursor-help"
      >
        {children}
      </span>
      {show && (
        <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 p-3 rounded-lg shadow-xl
                      bg-gray-900 border border-gray-700 text-xs text-gray-200 pointer-events-none">
          <div className="font-semibold text-sm mb-1 text-cyan-400">{entry.term}</div>
          <p className="mb-1">{entry.definition}</p>
          <p className="text-gray-400">{entry.interpretation}</p>
          {entry.good_range && (
            <p className="mt-1 text-gray-500">Typical range: <span className="text-gray-300">{entry.good_range}</span></p>
          )}
        </div>
      )}
    </span>
  );
}
