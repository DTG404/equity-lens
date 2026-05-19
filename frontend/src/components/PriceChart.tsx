'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  createChart,
  ColorType,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  AreaSeries,
  BarSeries,
  type ISeriesApi,
  type IChartApi,
} from 'lightweight-charts';
import ChartTypeSelector from './ChartTypeSelector';
import IndicatorOverlay from './IndicatorOverlay';
import SubChart from './SubChart';

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

function calcSma(data: number[], period: number): (number | null)[] {
  const out: (number | null)[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) { out.push(null); continue; }
    let sum = 0;
    for (let j = 0; j < period; j++) sum += data[i - j];
    out.push(sum / period);
  }
  return out;
}

function calcEma(data: number[], period: number): (number | null)[] {
  const out: (number | null)[] = [];
  const k = 2 / (period + 1);
  let ema: number | null = null;
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) { out.push(null); continue; }
    if (ema === null) {
      let sum = 0;
      for (let j = 0; j < period; j++) sum += data[i - j];
      ema = sum / period;
    } else {
      ema = data[i] * k + ema * (1 - k);
    }
    out.push(ema);
  }
  return out;
}

function calcBollinger(
  data: number[],
  period = 20,
  mult = 2
): { sma: (number | null)[]; upper: (number | null)[]; lower: (number | null)[] } {
  const sma = calcSma(data, period);
  const upper: (number | null)[] = [];
  const lower: (number | null)[] = [];
  for (let i = 0; i < data.length; i++) {
    if (sma[i] === null) { upper.push(null); lower.push(null); continue; }
    let sumSq = 0;
    for (let j = 0; j < period; j++) {
      const diff = data[i - j] - (sma[i] as number);
      sumSq += diff * diff;
    }
    const std = Math.sqrt(sumSq / period);
    upper.push((sma[i] as number) + mult * std);
    lower.push((sma[i] as number) - mult * std);
  }
  return { sma, upper, lower };
}

function calcRsi(data: number[], period = 14): (number | null)[] {
  const out: (number | null)[] = [];
  let gains = 0;
  let losses = 0;
  for (let i = 1; i <= period; i++) {
    const change = data[i] - data[i - 1];
    if (change >= 0) gains += change; else losses -= change;
  }
  let avgGain = gains / period;
  let avgLoss = losses / period;
  for (let i = 0; i < data.length; i++) {
    if (i <= period) { out.push(null); continue; }
    const change = data[i] - data[i - 1];
    const gain = change > 0 ? change : 0;
    const loss = change < 0 ? -change : 0;
    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;
    if (avgLoss === 0) { out.push(100); continue; }
    const rs = avgGain / avgLoss;
    out.push(100 - 100 / (1 + rs));
  }
  return out;
}

export default function PriceChart({ data }: PriceChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const mainSeriesRef = useRef<ISeriesApi<'Candlestick'> | ISeriesApi<'Line'> | ISeriesApi<'Area'> | ISeriesApi<'Bar'> | null>(null);
  const volSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const indicatorSeriesRef = useRef<ISeriesApi<'Line'>[]>([]);

  const [chartType, setChartType] = useState('candlestick');
  const [showIndicators, setShowIndicators] = useState(false);
  const [visibleIndicators, setVisibleIndicators] = useState<Record<string, boolean>>({
    sma_20: false, sma_50: false, sma_200: false,
    ema_12: false, ema_26: false, bollinger: false,
  });
  const [drawingTool, setDrawingTool] = useState<string | null>(null);

  const toggleIndicator = useCallback((id: string) => {
    setVisibleIndicators(prev => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const closePrices = data.map(d => d.close);
  const times = data.map(d => d.date.slice(0, 10));

  const sma20 = calcSma(closePrices, 20);
  const sma50 = calcSma(closePrices, 50);
  const sma200 = calcSma(closePrices, 200);
  const ema12 = calcEma(closePrices, 12);
  const ema26 = calcEma(closePrices, 26);
  const bollinger = calcBollinger(closePrices, 20, 2);
  const rsi = calcRsi(closePrices, 14);

  const rsiData = times
    .map((time, i) => ({ time: time as any, value: rsi[i] }))
    .filter(d => d.value !== null) as { time: any; value: number }[];

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
    chartRef.current = chart;

    const volSeries = chart.addSeries(HistogramSeries, {
      color: 'rgba(74,222,128,0.2)', priceFormat: { type: 'volume' }, priceScaleId: 'volume',
    });
    volSeriesRef.current = volSeries;
    chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 }, borderColor: 'rgba(255,255,255,0.06)',
    });

    const volumeData = data.map((d) => ({
      time: d.date.slice(0, 10) as any, value: d.volume,
      color: d.close >= d.open ? 'rgba(74,222,128,0.2)' : 'rgba(248,113,113,0.2)',
    }));
    volSeries.setData(volumeData);

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
      mainSeriesRef.current = null;
      volSeriesRef.current = null;
      indicatorSeriesRef.current = [];
    };
  }, [data]);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart || data.length === 0) return;

    if (mainSeriesRef.current) {
      chart.removeSeries(mainSeriesRef.current);
      mainSeriesRef.current = null;
    }

    const timeData = data.map((d) => ({ time: d.date.slice(0, 10) as any }));

    if (chartType === 'candlestick') {
      const series = chart.addSeries(CandlestickSeries, {
        upColor: '#4ade80', downColor: '#f87171',
        borderUpColor: '#4ade80', borderDownColor: '#f87171',
        wickUpColor: '#4ade80', wickDownColor: '#f87171',
        priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
      });
      series.setData(data.map(d => ({
        time: d.date.slice(0, 10) as any,
        open: d.open, high: d.high, low: d.low, close: d.close,
      })));
      mainSeriesRef.current = series;
    } else if (chartType === 'line') {
      const series = chart.addSeries(LineSeries, {
        color: '#22d3ee', lineWidth: 2,
        priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
      });
      series.setData(data.map(d => ({ time: d.date.slice(0, 10) as any, value: d.close })));
      mainSeriesRef.current = series;
    } else if (chartType === 'area') {
      const series = chart.addSeries(AreaSeries, {
        lineColor: '#22d3ee', topColor: 'rgba(34,211,238,0.4)',
        bottomColor: 'rgba(34,211,238,0.0)', lineWidth: 2,
        priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
      });
      series.setData(data.map(d => ({ time: d.date.slice(0, 10) as any, value: d.close })));
      mainSeriesRef.current = series;
    } else if (chartType === 'bar') {
      const series = chart.addSeries(BarSeries, {
        upColor: '#4ade80', downColor: '#f87171',
        thinBars: false,
        priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
      });
      series.setData(data.map(d => ({
        time: d.date.slice(0, 10) as any,
        open: d.open, high: d.high, low: d.low, close: d.close,
      })));
      mainSeriesRef.current = series;
    }
  }, [chartType, data]);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart || data.length === 0) return;

    indicatorSeriesRef.current.forEach(s => chart.removeSeries(s));
    indicatorSeriesRef.current = [];

    const addIndicatorLine = (values: (number | null)[], color: string) => {
      const series = chart.addSeries(LineSeries, { color, lineWidth: 1, lastValueVisible: false, title: '' });
      const lineData = times
        .map((time, i) => ({ time: time as any, value: values[i] }))
        .filter(d => d.value !== null) as { time: any; value: number }[];
      series.setData(lineData);
      indicatorSeriesRef.current.push(series);
    };

    if (visibleIndicators.sma_20) addIndicatorLine(sma20, '#fbbf24');
    if (visibleIndicators.sma_50) addIndicatorLine(sma50, '#a78bfa');
    if (visibleIndicators.sma_200) addIndicatorLine(sma200, '#f472b6');
    if (visibleIndicators.ema_12) addIndicatorLine(ema12, '#34d399');
    if (visibleIndicators.ema_26) addIndicatorLine(ema26, '#60a5fa');
    if (visibleIndicators.bollinger) {
      addIndicatorLine(bollinger.sma, '#fbbf24');
      addIndicatorLine(bollinger.upper, 'rgba(251,191,36,0.4)');
      addIndicatorLine(bollinger.lower, 'rgba(251,191,36,0.4)');
    }
  }, [visibleIndicators, data]);

  if (data.length === 0) {
    return (
      <div data-testid="price-chart">
        <div className="flex h-[320px] items-center justify-center text-sm text-white/30">No price data available</div>
      </div>
    );
  }

  return (
    <div data-testid="price-chart">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <ChartTypeSelector active={chartType} onChange={setChartType} />
        <div className="h-3 w-px bg-white/10" />
        <button
          onClick={() => setShowIndicators(v => !v)}
          className={`px-1.5 py-0.5 text-[0.55rem] font-mono rounded transition-colors border ${
            showIndicators ? 'bg-cyan-400/10 text-cyan-400 border-cyan-400/30' : 'text-white/30 border-white/10 hover:text-white/60'
          }`}
        >
          Indicators
        </button>
        <div className="flex gap-0.5">
          {[
            { id: 'trend', icon: '/' },
            { id: 'horizontal', icon: '—' },
            { id: 'rect', icon: '□' },
            { id: 'text', icon: 'T' },
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setDrawingTool(prev => prev === t.id ? null : t.id)}
              className={`px-1.5 py-0.5 text-[0.55rem] font-mono rounded transition-colors ${
                drawingTool === t.id ? 'bg-cyan-400/10 text-cyan-400' : 'text-white/30 hover:text-white/60'
              }`}
            >
              {t.icon}
            </button>
          ))}
        </div>
      </div>

      {showIndicators && (
        <div className="mb-2">
          <IndicatorOverlay visible={visibleIndicators} onToggle={toggleIndicator} />
        </div>
      )}

      <div ref={chartContainerRef} className="w-full" style={{ height: 320 }} />

      <SubChart data={rsiData} label="RSI" color="#60a5fa" height={70} />
    </div>
  );
}
