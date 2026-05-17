import React from 'react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import SignalHistory from '../src/components/SignalHistory';
import * as api from '../src/lib/api';

vi.mock('../src/lib/api', async () => {
  const actual = await vi.importActual<typeof import('../src/lib/api')>('../src/lib/api');
  return {
    ...actual,
    fetchSignalOutcomes: vi.fn(),
    fetchSignalMetrics: vi.fn(),
  };
});

const mockOutcomes: api.SignalOutcome[] = [
  {
    id: 1,
    symbol: 'AAPL',
    stance: 'bullish',
    confidence: 0.75,
    price_at_analysis: 180.0,
    window: '1d',
    price_at_check: 185.0,
    return_pct: 2.78,
    correct: true,
    checked_at: '2026-05-15T10:00:00Z',
  },
  {
    id: 2,
    symbol: 'AAPL',
    stance: 'bearish',
    confidence: 0.6,
    price_at_analysis: 190.0,
    window: '1w',
    price_at_check: 188.0,
    return_pct: -1.05,
    correct: true,
    checked_at: '2026-05-10T10:00:00Z',
  },
  {
    id: 3,
    symbol: 'AAPL',
    stance: 'bullish',
    confidence: 0.8,
    price_at_analysis: 175.0,
    window: '1d',
    price_at_check: 172.0,
    return_pct: -1.71,
    correct: false,
    checked_at: '2026-05-14T10:00:00Z',
  },
];

const mockMetrics: api.SignalMetrics = {
  total_signals: 3,
  correct_count: 2,
  accuracy_pct: 66.67,
  avg_return: 0.01,
};

describe('SignalHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders accuracy metric', async () => {
    vi.mocked(api.fetchSignalOutcomes).mockResolvedValue(mockOutcomes);
    vi.mocked(api.fetchSignalMetrics).mockResolvedValue(mockMetrics);

    render(<SignalHistory symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByTestId('accuracy-metric')).toBeDefined();
      expect(screen.getByTestId('accuracy-metric').textContent).toContain('66.67%');
    });
  });

  it('renders signal count and average return', async () => {
    vi.mocked(api.fetchSignalOutcomes).mockResolvedValue(mockOutcomes);
    vi.mocked(api.fetchSignalMetrics).mockResolvedValue(mockMetrics);

    render(<SignalHistory symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByTestId('signals-count')).toBeDefined();
      expect(screen.getByTestId('signals-count').textContent).toContain('3');
      expect(screen.getByTestId('avg-return')).toBeDefined();
      expect(screen.getByTestId('avg-return').textContent).toContain('0.01%');
    });
  });

  it('renders signal outcome table with correct columns', async () => {
    vi.mocked(api.fetchSignalOutcomes).mockResolvedValue(mockOutcomes);
    vi.mocked(api.fetchSignalMetrics).mockResolvedValue(mockMetrics);

    render(<SignalHistory symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText('Symbol')).toBeDefined();
      expect(screen.getByText('Stance')).toBeDefined();
      expect(screen.getByText('Window')).toBeDefined();
      expect(screen.getByText('Return')).toBeDefined();
      expect(screen.getByText('Result')).toBeDefined();
    });
  });

  it('renders correct badge for correct signals', async () => {
    vi.mocked(api.fetchSignalOutcomes).mockResolvedValue(mockOutcomes);
    vi.mocked(api.fetchSignalMetrics).mockResolvedValue(mockMetrics);

    render(<SignalHistory symbol="AAPL" />);

    await waitFor(() => {
      const correctBadges = screen.getAllByText('Correct');
      expect(correctBadges.length).toBe(2);
    });
  });

  it('renders incorrect badge for incorrect signals', async () => {
    vi.mocked(api.fetchSignalOutcomes).mockResolvedValue(mockOutcomes);
    vi.mocked(api.fetchSignalMetrics).mockResolvedValue(mockMetrics);

    render(<SignalHistory symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText('Incorrect')).toBeDefined();
    });
  });

  it('shows empty state when no outcomes', async () => {
    vi.mocked(api.fetchSignalOutcomes).mockResolvedValue([]);
    vi.mocked(api.fetchSignalMetrics).mockResolvedValue({
      total_signals: 0,
      correct_count: 0,
      accuracy_pct: 0,
      avg_return: 0,
    });

    render(<SignalHistory symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText(/No signal outcomes/)).toBeDefined();
    });
  });

  it('calls fetchSignalOutcomes with symbol filter', async () => {
    vi.mocked(api.fetchSignalOutcomes).mockResolvedValue(mockOutcomes);
    vi.mocked(api.fetchSignalMetrics).mockResolvedValue(mockMetrics);

    render(<SignalHistory symbol="AAPL" />);

    await waitFor(() => {
      expect(api.fetchSignalOutcomes).toHaveBeenCalledWith('AAPL');
    });
  });
});
