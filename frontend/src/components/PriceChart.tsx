'use client';

import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CandlestickSeries, HistogramSeries } from 'lightweight-charts';

export interface PriceChartPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface PriceChartProps {
  data: PriceChartPoint[];
}

export default function PriceChart({ data }: PriceChartProps) {
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
      rightPriceScale: { borderColor: 'rgba(255,255,255,0.06)', scaleMargins: { top: 0.1, bottom: 0.25 } },
      timeScale: { borderColor: 'rgba(255,255,255,0.06)', timeVisible: false, ticksVisible: true },
      handleScroll: false,
      handleScale: false,
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#4ade80', downColor: '#f87171',
      borderUpColor: '#4ade80', borderDownColor: '#f87171',
      wickUpColor: '#4ade80', wickDownColor: '#f87171',
      priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
    });

    const volSeries = chart.addSeries(HistogramSeries, {
      color: 'rgba(74,222,128,0.2)', priceFormat: { type: 'volume' }, priceScaleId: 'volume',
    });

    chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 }, borderColor: 'rgba(255,255,255,0.06)',
    });

    const candleData = data.map((d) => ({ time: d.date.slice(0, 10) as any, open: d.open, high: d.high, low: d.low, close: d.close }));
    const volumeData = data.map((d) => ({
      time: d.date.slice(0, 10) as any, value: d.volume,
      color: d.close >= d.open ? 'rgba(74,222,128,0.2)' : 'rgba(248,113,113,0.2)',
    }));

    candleSeries.setData(candleData);
    volSeries.setData(volumeData);
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
    return <div className="flex h-[320px] items-center justify-center text-sm text-white/30">No price data available</div>;
  }

  return (
    <div data-testid="price-chart">
      <div ref={chartContainerRef} className="w-full" style={{ height: 320 }} />
    </div>
  );
}
