import React from 'react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import ResearchPage from '../app/stocks/[symbol]/page';
import * as api from '../src/lib/api';

vi.mock('../src/lib/api', async () => {
  const actual = await vi.importActual<typeof import('../src/lib/api')>('../src/lib/api');
  return {
    ...actual,
    fetchResearch: vi.fn(),
    fetchSignalOutcomes: vi.fn(),
    fetchSignalMetrics: vi.fn(),
  };
});

vi.mock('next/navigation', () => ({
  usePathname: () => '/',
  useRouter: () => ({ push: vi.fn(), prefetch: vi.fn() }),
}));

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) =>
    React.createElement('a', { href }, children),
}));

// Mock lightweight-charts (requires Canvas API not available in jsdom)
vi.mock('lightweight-charts', () => ({
  createChart: () => ({
    addSeries: () => ({ setData: vi.fn() }),
    priceScale: () => ({ applyOptions: vi.fn() }),
    timeScale: () => ({ fitContent: vi.fn() }),
    applyOptions: vi.fn(),
    remove: vi.fn(),
  }),
  ColorType: { Solid: 'Solid' },
  CandlestickSeries: 'CandlestickSeries' as any,
  HistogramSeries: 'HistogramSeries' as any,
}));

const today = new Date();
const daysAgo = (n: number) => {
  const d = new Date(today);
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
};

const mockResearchData: api.ResearchData = {
  symbol: 'AAPL',
  quote: {
    symbol: 'AAPL',
    price: 185.5,
    change_percent: 1.25,
    provider: 'mock',
  },
  price_history: [
    { date: daysAgo(2), open: 180, high: 182, low: 179, close: 181, volume: 1000000 },
    { date: daysAgo(1), open: 181, high: 184, low: 180, close: 183, volume: 1200000 },
    { date: daysAgo(0), open: 183, high: 186, low: 182, close: 185.5, volume: 1100000 },
  ],
  news: [
    {
      id: 1,
      symbol: 'AAPL',
      title: 'Apple Reports Record Earnings',
      url: 'https://example.com/apple-earnings',
      source: 'Yahoo Finance',
      summary: 'Apple beat expectations...',
      published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
  ],
  scores: {
    technical: { score: 0.72, explanation: 'Based on recent price momentum and volume trends.' },
    news_sentiment: { score: 0.61, explanation: 'Aggregated sentiment from recent news coverage.' },
    fundamentals: { score: 0.55, explanation: 'Valuation metrics and earnings trajectory.' },
    macro: { score: 0.48, explanation: 'Sector and macroeconomic conditions.' },
    overall: 0.6,
  },
  thesis: 'AAPL shows a neutral outlook with a composite score of 60%.',
  risks: 'Key risks include sector headwinds, macroeconomic uncertainty, and company-specific execution risk.',
  scenarios: {
    bull_case: 'Bullish scenario: strong earnings growth drives price to $220.',
    base_case: 'Base case: steady performance maintains price around $185.',
    bear_case: 'Bear case: margin compression pushes price down to $150.',
    model: 'deepseek-chat',
  },
  analysis_id: 1,
  analysis_created_at: '2026-05-17T10:00:00Z',
};

const mockSignalOutcomes: api.SignalOutcome[] = [
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
];

const mockSignalMetrics: api.SignalMetrics = {
  total_signals: 1,
  correct_count: 1,
  accuracy_pct: 100.0,
  avg_return: 2.78,
};

describe('ResearchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.fetchSignalOutcomes).mockResolvedValue(mockSignalOutcomes);
    vi.mocked(api.fetchSignalMetrics).mockResolvedValue(mockSignalMetrics);
  });

  it('renders symbol header with price and change percent', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getAllByText('AAPL').length).toBeGreaterThan(0);
      expect(screen.getByText('$185.50')).toBeDefined();
      expect(screen.getByText('+1.25%')).toBeDefined();
    });
  });

  it('renders price chart', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByTestId('price-chart')).toBeDefined();
    });
  });

  it('renders factor scores', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByText('Technical')).toBeDefined();
      expect(screen.getByText('News Sentiment')).toBeDefined();
      expect(screen.getByText('Fundamentals')).toBeDefined();
      expect(screen.getByText('Macro')).toBeDefined();
      expect(screen.getByText('Overall')).toBeDefined();
    });
  });

  it('renders thesis section', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByText(/AI Thesis/i)).toBeDefined();
      expect(screen.getByText(mockResearchData.thesis)).toBeDefined();
    });
  });

  it('renders risks section', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      const risks = screen.getAllByText(/Risks/i);
      expect(risks.length).toBeGreaterThan(0);
      expect(screen.getByText(mockResearchData.risks)).toBeDefined();
    });
  });

  it('renders back to dashboard link', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getAllByText(/Dashboard/i).length).toBeGreaterThan(0);
    });
  });

  it('renders bull, base, and bear scenarios', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByText('Bull Case')).toBeDefined();
      expect(screen.getByText(mockResearchData.scenarios.bull_case)).toBeDefined();
      expect(screen.getByText('Base Case')).toBeDefined();
      expect(screen.getByText(mockResearchData.scenarios.base_case)).toBeDefined();
      expect(screen.getByText('Bear Case')).toBeDefined();
      expect(screen.getByText(mockResearchData.scenarios.bear_case)).toBeDefined();
    });
  });

  it('renders analysis metadata', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByText(/Model: deepseek-chat/)).toBeDefined();
      expect(screen.getByText(/Analysis #1/)).toBeDefined();
    });
  });

  it('renders regenerate analysis button', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Regenerate/i })).toBeDefined();
    });
  });

  it('re-fetches research when regenerate button is clicked', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Regenerate/i })).toBeDefined();
    });

    const button = screen.getByRole('button', { name: /Regenerate/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(api.fetchResearch).toHaveBeenCalledTimes(2);
    });
  });

  it('renders signal history section', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByText(/Signal History/i)).toBeDefined();
    });
  });

  it('renders accuracy metric in signal history', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(screen.getByTestId('accuracy-metric')).toBeDefined();
      expect(screen.getByTestId('accuracy-metric').textContent).toContain('100.00%');
    });
  });

  it('calls fetchSignalOutcomes with current symbol', async () => {
    vi.mocked(api.fetchResearch).mockResolvedValue(mockResearchData);

    render(<ResearchPage params={Promise.resolve({ symbol: 'AAPL' })} />);

    await waitFor(() => {
      expect(api.fetchSignalOutcomes).toHaveBeenCalledWith('AAPL');
    });
  });
});
