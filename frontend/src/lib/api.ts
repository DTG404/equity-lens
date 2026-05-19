const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export interface WatchlistItem {
  symbol: string;
  company_name: string;
  price: number | null;
  change_percent: number | null;
  signal?: string | null;
  confidence?: number | null;
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

export async function fetchResearch(symbol: string, force?: boolean): Promise<ResearchData> {
  const url = force ? `${API_BASE}/api/research/${symbol}?force=true` : `${API_BASE}/api/research/${symbol}`;
  const response = await fetch(url);
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

/* ── Fundamentals (SEC EDGAR) ──────────────────────────────── */

export interface FundamentalsData {
  symbol: string;
  income_statement: {
    revenue: number | null;
    gross_profit: number | null;
    operating_income: number | null;
    net_income: number | null;
  };
  balance_sheet: {
    total_assets: number | null;
    total_liabilities: number | null;
    current_assets: number | null;
    current_liabilities: number | null;
    equity: number | null;
    long_term_debt: number | null;
  };
  cash_flow: {
    operating_cash_flow: number | null;
    free_cash_flow: number | null;
  };
  per_share: {
    eps_basic: number | null;
    eps_diluted: number | null;
  };
  ratios: {
    debt_to_equity: number | null;
    current_ratio: number | null;
    net_margin: number | null;
    gross_margin: number | null;
  };
}

export async function fetchFundamentals(symbol: string): Promise<FundamentalsData> {
  const response = await fetch(`${API_BASE}/api/fundamentals/${symbol}`);
  if (!response.ok) throw new Error('Failed to fetch fundamentals');
  return response.json() as Promise<FundamentalsData>;
}

/* ── Technical Indicators (TA-Lib) ─────────────────────────── */

export interface TechnicalsData {
  symbol: string;
  rsi: number | null;
  macd: {
    macd_line: number | null;
    signal_line: number | null;
    histogram: number | null;
  };
  moving_averages: {
    sma_20: number | null;
    sma_50: number | null;
    sma_200: number | null;
    ema_12: number | null;
    ema_26: number | null;
  };
  bollinger_bands: {
    upper: number | null;
    middle: number | null;
    lower: number | null;
  };
  atr: number | null;
}

export async function fetchTechnicals(symbol: string): Promise<TechnicalsData> {
  const response = await fetch(`${API_BASE}/api/technicals/${symbol}`);
  if (!response.ok) throw new Error('Failed to fetch technicals');
  return response.json() as Promise<TechnicalsData>;
}

/* ── Macro Dashboard (FRED) ────────────────────────────────── */

export interface MacroIndicator {
  name: string;
  value: number;
  previous: number | null;
  change: number | null;
  unit: string;
}

export interface MacroData {
  source: string;
  note?: string;
  indicators: Record<string, MacroIndicator>;
}

export async function fetchMacro(): Promise<MacroData> {
  const response = await fetch(`${API_BASE}/api/macro`);
  if (!response.ok) throw new Error('Failed to fetch macro data');
  return response.json() as Promise<MacroData>;
}

/* ── Stock Screener ────────────────────────────────────────── */

export interface ScreenerResult {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  volume: number;
  sector: string;
  market_cap: number | null;
  pe_ratio: number | null;
  rsi: number | null;
}

export interface ScreenerResponse {
  total: number;
  returned: number;
  errors: number;
  results: ScreenerResult[];
}

/* ── Portfolio Performance ─────────────────────────────────── */

export interface PortfolioPosition {
  symbol: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  cost_basis: number;
  market_value: number;
  pl: number;
  pl_pct: number;
}

export interface PortfolioPerformance {
  total_cost: number;
  total_value: number;
  total_pl: number;
  total_pl_pct: number;
  position_count: number;
  positions: PortfolioPosition[];
}

export async function fetchPortfolioPerformance(): Promise<PortfolioPerformance> {
  const response = await fetch(`${API_BASE}/api/portfolio/performance`);
  if (!response.ok) throw new Error('Failed to fetch portfolio performance');
  return response.json() as Promise<PortfolioPerformance>;
}

/* ── Portfolio Analytics ───────────────────────────────────── */

export interface AllocationItem {
  symbol: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  pct: number;
  sector: string;
}

export interface SectorAllocation {
  sector: string;
  market_value: number;
  pct: number;
}

export interface PortfolioAnalytics {
  allocation: {
    by_ticker: AllocationItem[];
    by_sector: SectorAllocation[];
    total_value: number;
  };
  value_history: { date: string; value: number }[];
  benchmark: null;
}

export async function fetchPortfolioAnalytics(): Promise<PortfolioAnalytics> {
  const response = await fetch(`${API_BASE}/api/portfolio/analytics`);
  if (!response.ok) throw new Error('Failed to fetch portfolio analytics');
  return response.json() as Promise<PortfolioAnalytics>;
}

export interface ExplainData {
  explanation: string;
  key_takeaways: string[];
  questions_to_ask: string[];
}

export async function fetchExplanation(symbol: string): Promise<ExplainData> {
  const response = await fetch(`${API_BASE}/api/research/${symbol}/explain`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to fetch explanation');
  return response.json() as Promise<ExplainData>;
}

export async function fetchScreener(params?: {
  priceMin?: number;
  priceMax?: number;
  sector?: string;
  rsiMin?: number;
  rsiMax?: number;
  volumeMin?: number;
  sortBy?: string;
  sortDir?: string;
  limit?: number;
  skip?: number;
}): Promise<ScreenerResponse> {
  const query = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null) query.set(key, String(val));
    });
  }
  const response = await fetch(`${API_BASE}/api/screener?${query}`);
  if (!response.ok) throw new Error('Failed to fetch screener data');
  return response.json() as Promise<ScreenerResponse>;
}
