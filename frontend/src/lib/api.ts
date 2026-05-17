const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export interface WatchlistItem {
  symbol: string;
  company_name: string;
  price: number | null;
  change_percent: number | null;
}

export interface Quote {
  symbol: string;
  price: number;
  change_percent: number;
  provider: string;
}

export interface NewsArticle {
  id: number;
  symbol: string;
  title: string;
  url: string;
  source: string;
  summary: string;
  published_at: string | null;
}

export interface FactorScore {
  score: number;
  explanation: string;
}

export interface ResearchData {
  symbol: string;
  quote: {
    symbol: string;
    price: number;
    change_percent: number;
    provider: string;
  } | null;
  price_history: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  news: NewsArticle[];
  scores: {
    technical: FactorScore;
    news_sentiment: FactorScore;
    fundamentals: FactorScore;
    macro: FactorScore;
    overall: number;
  };
  thesis: string;
  risks: string;
  scenarios: {
    bull_case: string;
    base_case: string;
    bear_case: string;
    model: string;
  };
  analysis_id: number;
  analysis_created_at: string;
}

export interface HoldingItem {
  id: number;
  symbol: string;
  quantity: number;
  average_cost: number;
  notes: string;
}

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  const response = await fetch(`${API_BASE}/api/watchlist`);
  if (!response.ok) {
    throw new Error(`Failed to fetch watchlist: ${response.statusText}`);
  }
  return response.json() as Promise<WatchlistItem[]>;
}

export async function addToWatchlist(symbol: string, companyName?: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/watchlist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, company_name: companyName ?? '' }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || 'Failed to add to watchlist');
  }
}

export async function removeFromWatchlist(symbol: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/watchlist/${symbol}`, { method: 'DELETE' });
  if (!response.ok) throw new Error('Failed to remove from watchlist');
}

export async function fetchHoldings(): Promise<HoldingItem[]> {
  const response = await fetch(`${API_BASE}/api/holdings`);
  if (!response.ok) throw new Error('Failed to fetch holdings');
  return response.json() as Promise<HoldingItem[]>;
}

export async function addHolding(symbol: string, quantity: number, averageCost: number): Promise<void> {
  const response = await fetch(`${API_BASE}/api/holdings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, quantity, average_cost: averageCost }),
  });
  if (!response.ok) throw new Error('Failed to add holding');
}

export async function fetchQuote(symbol: string): Promise<Quote> {
  const response = await fetch(`${API_BASE}/api/quotes/${symbol}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch quote: ${response.statusText}`);
  }
  return response.json() as Promise<Quote>;
}

export async function healthCheck(): Promise<{ service: string; status: string; mode: string }> {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json() as Promise<{ service: string; status: string; mode: string }>;
}

export async function fetchNews(symbol?: string): Promise<NewsArticle[]> {
  const url = symbol
    ? `${API_BASE}/api/news/${symbol}`
    : `${API_BASE}/api/news`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch news');
  return response.json() as Promise<NewsArticle[]>;
}

export async function fetchResearch(symbol: string): Promise<ResearchData> {
  const response = await fetch(`${API_BASE}/api/research/${symbol}`);
  if (!response.ok) throw new Error('Failed to fetch research data');
  return response.json() as Promise<ResearchData>;
}

export async function fetchSignalOutcomes(symbol?: string): Promise<SignalOutcome[]> {
  const url = symbol
    ? `${API_BASE}/api/signals/outcomes?symbol=${encodeURIComponent(symbol)}`
    : `${API_BASE}/api/signals/outcomes`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch signal outcomes');
  return response.json() as Promise<SignalOutcome[]>;
}

export async function fetchSignalMetrics(): Promise<SignalMetrics> {
  const response = await fetch(`${API_BASE}/api/signals/metrics`);
  if (!response.ok) throw new Error('Failed to fetch signal metrics');
  return response.json() as Promise<SignalMetrics>;
}

export interface SignalOutcome {
  id: number;
  symbol: string;
  stance: string;
  confidence: number;
  price_at_analysis: number;
  window: string;
  price_at_check: number;
  return_pct: number;
  correct: boolean;
  checked_at: string;
}

export interface SignalMetrics {
  total_signals: number;
  correct_count: number;
  accuracy_pct: number;
  avg_return: number;
}

export interface AlertRule {
  id: number;
  symbol: string;
  alert_type: string;
  condition: string;
  threshold: number;
  enabled: boolean;
  created_at: string;
}

export interface AlertEvent {
  id: number;
  symbol: string;
  alert_type: string;
  message: string;
  severity: string;
  read: boolean;
  triggered_at: string;
}

export async function fetchAlertRules(): Promise<AlertRule[]> {
  const response = await fetch(`${API_BASE}/api/alerts/rules`);
  if (!response.ok) throw new Error('Failed to fetch alert rules');
  return response.json() as Promise<AlertRule[]>;
}

export async function createAlertRule(
  symbol: string,
  alertType: string,
  condition: string,
  threshold: number,
): Promise<AlertRule> {
  const response = await fetch(`${API_BASE}/api/alerts/rules`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, alert_type: alertType, condition, threshold }),
  });
  if (!response.ok) throw new Error('Failed to create alert rule');
  return response.json() as Promise<AlertRule>;
}

export async function deleteAlertRule(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/api/alerts/rules/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete alert rule');
}

export async function fetchAlertEvents(): Promise<AlertEvent[]> {
  const response = await fetch(`${API_BASE}/api/alerts/events`);
  if (!response.ok) throw new Error('Failed to fetch alert events');
  return response.json() as Promise<AlertEvent[]>;
}

export async function fetchUnreadAlertCount(): Promise<number> {
  const response = await fetch(`${API_BASE}/api/alerts/events/unread-count`);
  if (!response.ok) throw new Error('Failed to fetch unread alert count');
  const data = await response.json() as { count: number };
  return data.count;
}

export async function markAlertRead(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/api/alerts/events/${id}/read`, {
    method: 'PATCH',
  });
  if (!response.ok) throw new Error('Failed to mark alert as read');
}

export async function markAllAlertsRead(): Promise<void> {
  const response = await fetch(`${API_BASE}/api/alerts/events/read-all`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to mark all alerts as read');
}
