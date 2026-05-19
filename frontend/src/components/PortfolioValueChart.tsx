'use client';

import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, AreaSeries } from 'lightweight-charts';

export interface ValueHistoryPoint {
  date: string;
  value: number;
}

interface PortfolioValueChartProps {
  data: ValueHistoryPoint[];
}

export default function PortfolioValueChart({ data }: PortfolioValueChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

    const container = chartContainerRef.current;
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 320,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: 'rgba(255,255,255,0.4)',
        fontSize: 11,
        fontFamily: "'JetBrains Mono', monospace",
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.03)' },
        horzLines: { color: 'rgba(255,255,255,0.03)' },
      },
      crosshair: {
        mode: 0,
        vertLine: { color: 'rgba(34,211,238,0.4)', width: 1, style: 2, labelBackgroundColor: 'rgba(34,211,238,0.2)' },
        horzLine: { color: 'rgba(34,211,238,0.4)', width: 1, style: 2, labelBackgroundColor: 'rgba(34,211,238,0.2)' },
      },
      rightPriceScale: { borderColor: 'rgba(255,255,255,0.06)', scaleMargins: { top: 0.1, bottom: 0.1 } },
      timeScale: { borderColor: 'rgba(255,255,255,0.06)', timeVisible: false, ticksVisible: true },
      handleScroll: false,
      handleScale: false,
    });

    const areaSeries = chart.addSeries(AreaSeries, {
      lineColor: '#4ade80',
      topColor: 'rgba(74, 222, 128, 0.4)',
      bottomColor: 'rgba(74, 222, 128, 0.0)',
      lineWidth: 2,
      priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
    });

    const chartData = data.map((d) => ({
      time: d.date.slice(0, 10) as unknown as string,
      value: d.value,
    }));

    areaSeries.setData(chartData);
    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data]);

  if (data.length === 0) {
    return (
      <div className="glass-panel flex h-[320px] items-center justify-center">
        <span className="text-sm text-white/30">No portfolio history yet</span>
      </div>
    );
  }

  return (
    <div data-testid="portfolio-value-chart">
      <div ref={chartContainerRef} className="w-full" style={{ height: 320 }} />
    </div>
  );
}
