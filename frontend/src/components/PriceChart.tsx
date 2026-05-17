'use client';

import React from 'react';

export interface PriceChartPoint {
  date: string;
  close: number;
}

interface PriceChartProps {
  data: PriceChartPoint[];
  width?: number;
  height?: number;
}

export default function PriceChart({
  data,
  width = 600,
  height = 300,
}: PriceChartProps) {
  if (data.length === 0) {
    return (
      <div
        data-testid="price-chart"
        style={{
          width,
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-secondary)',
          fontSize: 14,
        }}
      >
        No price data available
      </div>
    );
  }

  const padding = { top: 20, right: 20, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const prices = data.map((d) => d.close);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice || 1;

  const scaleX = (index: number) =>
    padding.left + (index / (data.length - 1 || 1)) * chartWidth;
  const scaleY = (price: number) =>
    padding.top + chartHeight - ((price - minPrice) / priceRange) * chartHeight;

  const linePath = data
    .map((d, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i)} ${scaleY(d.close)}`)
    .join(' ');

  const yTicks = 5;
  const yTickValues = Array.from({ length: yTicks + 1 }, (_, i) =>
    minPrice + (priceRange * i) / yTicks,
  );

  return (
    <div data-testid="price-chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: 'auto', maxWidth: width }}
        role="img"
        aria-label="Price chart"
      >
        {yTickValues.map((tick, i) => (
          <line
            key={`grid-${i}`}
            x1={padding.left}
            y1={scaleY(tick)}
            x2={padding.left + chartWidth}
            y2={scaleY(tick)}
            stroke="var(--border)"
            strokeWidth={1}
            strokeDasharray="4 4"
          />
        ))}

        <line
          x1={padding.left}
          y1={padding.top + chartHeight}
          x2={padding.left + chartWidth}
          y2={padding.top + chartHeight}
          stroke="var(--text-secondary)"
          strokeWidth={1}
        />

        {yTickValues.map((tick, i) => (
          <text
            key={`y-label-${i}`}
            x={padding.left - 10}
            y={scaleY(tick)}
            textAnchor="end"
            dominantBaseline="middle"
            fill="var(--text-secondary)"
            fontSize={11}
          >
            {tick.toFixed(2)}
          </text>
        ))}

        {[0, Math.floor((data.length - 1) / 2), data.length - 1].map((index) => (
          <text
            key={`x-label-${index}`}
            x={scaleX(index)}
            y={height - 10}
            textAnchor="middle"
            fill="var(--text-secondary)"
            fontSize={11}
          >
            {data[index].date}
          </text>
        ))}

        <path
          d={linePath}
          fill="none"
          stroke="var(--accent-blue, #3b82f6)"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {data.map((d, i) => (
          <circle
            key={`point-${i}`}
            cx={scaleX(i)}
            cy={scaleY(d.close)}
            r={3}
            fill="var(--accent-blue, #3b82f6)"
            stroke="var(--bg-card, #fff)"
            strokeWidth={1}
          />
        ))}
      </svg>
    </div>
  );
}
