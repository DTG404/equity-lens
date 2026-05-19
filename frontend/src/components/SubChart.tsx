'use client';

import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, LineSeries } from 'lightweight-charts';

interface Props {
  data: { time: string; value: number }[];
  color?: string;
  label: string;
  height?: number;
}

export default function SubChart({ data, color = '#60a5fa', label, height = 80 }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current || data.length === 0) return;
    const chart = createChart(ref.current, {
      width: ref.current.clientWidth,
      height,
      layout: { background: { type: ColorType.Solid, color: 'transparent' }, textColor: 'rgba(255,255,255,0.3)', fontSize: 10 },
      grid: { vertLines: { color: 'rgba(255,255,255,0.03)' }, horzLines: { color: 'rgba(255,255,255,0.03)' } },
      rightPriceScale: { borderColor: 'rgba(255,255,255,0.06)', visible: false },
      timeScale: { borderColor: 'rgba(255,255,255,0.06)', visible: false },
      handleScroll: false, handleScale: false,
    });
    const series = chart.addSeries(LineSeries, { color, lineWidth: 1 });
    series.setData(data);
    chart.timeScale().fitContent();
    const handleResize = () => { if (ref.current) chart.applyOptions({ width: ref.current.clientWidth }); };
    window.addEventListener('resize', handleResize);
    return () => { window.removeEventListener('resize', handleResize); chart.remove(); };
  }, [data, color, height]);

  if (data.length === 0) return null;

  return (
    <div className="border-t border-white/[0.04] px-2 pt-2 pb-1">
      <div className="text-[0.5rem] uppercase text-white/20 mb-1">{label}</div>
      <div ref={ref} />
    </div>
  );
}
