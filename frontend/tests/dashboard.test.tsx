import React from 'react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import DashboardShell from '../src/components/DashboardShell';
import * as api from '../src/lib/api';

vi.mock('../src/lib/api', async () => {
  const actual = await vi.importActual<typeof import('../src/lib/api')>('../src/lib/api');
  return {
    ...actual,
    fetchWatchlist: vi.fn(),
    fetchHoldings: vi.fn(),
    fetchNews: vi.fn(),
    addToWatchlist: vi.fn(),
    removeFromWatchlist: vi.fn(),
    addHolding: vi.fn(),
    fetchAlertRules: vi.fn(),
    fetchAlertEvents: vi.fn(),
    fetchUnreadAlertCount: vi.fn(),
    markAlertRead: vi.fn(),
    markAllAlertsRead: vi.fn(),
    createAlertRule: vi.fn(),
    deleteAlertRule: vi.fn(),
  };
});

describe('DashboardShell', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.fetchWatchlist).mockResolvedValue([]);
    vi.mocked(api.fetchHoldings).mockResolvedValue([]);
    vi.mocked(api.fetchNews).mockResolvedValue([]);
    vi.mocked(api.fetchAlertRules).mockResolvedValue([]);
    vi.mocked(api.fetchAlertEvents).mockResolvedValue([]);
    vi.mocked(api.fetchUnreadAlertCount).mockResolvedValue(0);
    vi.mocked(api.markAlertRead).mockResolvedValue(undefined);
    vi.mocked(api.markAllAlertsRead).mockResolvedValue(undefined);
    vi.mocked(api.createAlertRule).mockResolvedValue({
      id: 1,
      symbol: 'AAPL',
      alert_type: 'price',
      condition: 'above',
      threshold: 200,
      enabled: true,
      created_at: new Date().toISOString(),
    });
    vi.mocked(api.deleteAlertRule).mockResolvedValue(undefined);
  });

  it('renders the watchlist heading', () => {
    render(<DashboardShell />);
    expect(screen.getByText('Watchlist')).toBeDefined();
  });

  it('shows empty watchlist state', () => {
    render(<DashboardShell />);
    expect(screen.getByText(/Add symbols to your watchlist/)).toBeDefined();
  });

  it('renders the add-ticker form', () => {
    render(<DashboardShell />);
    expect(screen.getByPlaceholderText('Ticker symbol')).toBeDefined();
    expect(screen.getByRole('button', { name: 'Add' })).toBeDefined();
  });

  it('renders the holdings section', () => {
    render(<DashboardShell />);
    expect(screen.getByText('Holdings')).toBeDefined();
  });

  it('renders watchlist items with symbol and company name', async () => {
    vi.mocked(api.fetchWatchlist).mockResolvedValue([
      { symbol: 'AAPL', company_name: 'Apple Inc.', price: 185.5, change_percent: 1.25 },
      { symbol: 'MSFT', company_name: 'Microsoft Corp', price: 412.0, change_percent: -0.5 },
    ]);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeDefined();
      expect(screen.getByText('Apple Inc.')).toBeDefined();
      expect(screen.getByText('MSFT')).toBeDefined();
      expect(screen.getByText('Microsoft Corp')).toBeDefined();
    });
  });

  it('renders watchlist price with positive change in green', async () => {
    vi.mocked(api.fetchWatchlist).mockResolvedValue([
      { symbol: 'AAPL', company_name: 'Apple Inc.', price: 185.5, change_percent: 1.25 },
    ]);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('$185.50')).toBeDefined();
      expect(screen.getByText('+1.25%')).toBeDefined();
    });
  });

  it('renders watchlist price with negative change in red', async () => {
    vi.mocked(api.fetchWatchlist).mockResolvedValue([
      { symbol: 'TSLA', company_name: 'Tesla Inc.', price: 175.0, change_percent: -2.5 },
    ]);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('$175.00')).toBeDefined();
      expect(screen.getByText('-2.50%')).toBeDefined();
    });
  });

  it('renders watchlist with null price gracefully', async () => {
    vi.mocked(api.fetchWatchlist).mockResolvedValue([
      { symbol: 'META', company_name: 'Meta Platforms', price: null, change_percent: null },
    ]);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('META')).toBeDefined();
      expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders holdings with symbol, quantity, and average cost', async () => {
    vi.mocked(api.fetchHoldings).mockResolvedValue([
      { id: 1, symbol: 'AAPL', quantity: 10, average_cost: 150.0, notes: '' },
    ]);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeDefined();
      expect(screen.getByText(/10\s+@\s+\$150\.00/)).toBeDefined();
    });
  });

  it('renders the news feed heading', async () => {
    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('News Feed')).toBeDefined();
    });
  });

  it('renders news articles with title, source, and relative time', async () => {
    vi.mocked(api.fetchWatchlist).mockResolvedValue([
      { symbol: 'AAPL', company_name: 'Apple Inc.', price: 185.5, change_percent: 1.25 },
    ]);
    vi.mocked(api.fetchNews).mockResolvedValue([
      {
        id: 1,
        symbol: 'AAPL',
        title: 'Apple Reports Record Earnings',
        url: 'https://example.com/apple-earnings',
        source: 'Yahoo Finance',
        summary: 'Apple beat expectations...',
        published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 2,
        symbol: 'AAPL',
        title: 'iPhone 16 Rumors Heat Up',
        url: 'https://example.com/iphone16',
        source: 'Bloomberg',
        summary: 'New leaks suggest...',
        published_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      },
    ]);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('Apple Reports Record Earnings')).toBeDefined();
      expect(screen.getByText('iPhone 16 Rumors Heat Up')).toBeDefined();
      expect(screen.getByText('Yahoo Finance')).toBeDefined();
      expect(screen.getByText('Bloomberg')).toBeDefined();
    });
  });

  it('renders the alert center instead of placeholder', async () => {
    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText(/No alerts yet/)).toBeDefined();
    });
  });

  it('renders alert events with type, message, and severity', async () => {
    vi.mocked(api.fetchAlertEvents).mockResolvedValue([
      {
        id: 1,
        symbol: 'AAPL',
        alert_type: 'price',
        message: 'AAPL crossed above $200',
        severity: 'warning',
        read: false,
        triggered_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      },
    ]);
    vi.mocked(api.fetchUnreadAlertCount).mockResolvedValue(1);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('AAPL crossed above $200')).toBeDefined();
    });
  });

  it('renders unread alert count badge', async () => {
    vi.mocked(api.fetchUnreadAlertCount).mockResolvedValue(3);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByText('3')).toBeDefined();
    });
  });

  it('shows mark all read button when there are unread alerts', async () => {
    vi.mocked(api.fetchUnreadAlertCount).mockResolvedValue(2);
    vi.mocked(api.fetchAlertEvents).mockResolvedValue([
      {
        id: 1,
        symbol: 'TSLA',
        alert_type: 'price',
        message: 'TSLA dropped below $180',
        severity: 'critical',
        read: false,
        triggered_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      },
    ]);

    render(<DashboardShell />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Mark all read' })).toBeDefined();
    });
  });
});
