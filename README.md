# Equity Lens

> AI-native, local-first stock research terminal.

Equity Lens is a futuristic financial research terminal with a liquid glass UI, AI-powered analysis, and local-first architecture. It combines real-time market data, SEC EDGAR fundamentals, 30 TA-Lib technical indicators, FRED macroeconomic data, market indices, cryptocurrency data, news intelligence, and DeepSeek-generated thesis analysis into a single desktop application. It places simulated paper trades through Alpaca for educational purposes. It does not provide financial advice.

---

## Features

### Data & Analysis
- **Watchlist management** — add/remove US stock tickers with live price tracking and AI signal badges
- **SEC EDGAR fundamentals** — revenue, net income, EPS, balance sheet, ratios, free cash flow, financial statements (free, audit-quality)
- **SEC filings browser** — view recent 10-K, 10-Q, 8-K filings in-app
- **Insider trading** — monitor Form 4 insider transactions per ticker
- **Institutional ownership** — track 13F filing data per ticker
- **DCF valuation** — automated fair value estimates from SEC EDGAR fundamentals
- **30 TA-Lib technical indicators** — RSI, MACD, SMA/EMA, Bollinger Bands, ATR, Stochastic, Williams %R, MFI, CCI, OBV, CMF, VWAP, Keltner Channels, Parabolic SAR, Ichimoku Cloud, ADX, Aroon, Elder-Ray, A/D Line, Ultimate Oscillator, TRIX, ROC, Momentum, Donchian Channels, KAMA, HMA, SuperTrend
- **Chart pattern recognition** — auto-detect double top/bottom, bull flags, hammers, shooting stars (10+ patterns)
- **FRED macroeconomic dashboard** — GDP, CPI, unemployment, Fed funds rate, Treasury yields, consumer sentiment
- **Market overview** — S&P 500, NASDAQ, DOW, VIX indices with market breadth and commodities
- **Sector performance** — ranked sector returns with 1d/1w/1m/1y timeframe selector
- **Social sentiment** — StockTwits bullish/bearish sentiment overlay
- **Stock screener** — 120-ticker universe (80 stocks + 40 ETFs), filtered by price, sector, RSI, volume, market cap, P/E, beta, short float, dividend yield, and more. Saved presets, CSV export.
- **Premium news** — Finnhub news provider with yfinance fallback
- **Earnings calendar** — upcoming earnings dates with consensus estimates
- **Earnings summaries** — AI-generated beat/miss analysis from historical earnings data
- **Dividend calendar** — dividend yield, payout ratio, ex-dividend dates, payment history per ticker
- **Short interest data** — short float %, days to cover, squeeze potential scoring
- **Cryptocurrency data** — BTC, ETH, SOL, XRP, ADA, DOT, LINK, AVAX, MATIC, DOGE via CoinGecko
- **AI-powered analysis** — DeepSeek-generated thesis with bull/base/bear scenarios and factor scoring
- **AI explain** — beginner-friendly explanations of stock analysis
- **Price chart** — interactive candlestick chart with volume histogram, drawing tools, indicator overlays (SMA/EMA/Bollinger), sub-charts (RSI), chart type selector (line/area/bar)
- **Multiticker comparison** — side-by-side comparison of 2-5 tickers on price, P/E, revenue growth, RSI, and more
- **Peer comparison** — auto-compare against top sector peers with percentile rankings
- **Analyst consensus** — buy/hold/sell ratings and price targets from Finnhub
- **Per-ticker news** — deduplicated financial news with sentiment scoring
- **Signal tracking** — 1d/1w/1m accuracy measurement with outcome logging
- **Signal backtesting** — aggregate accuracy and returns by stance and time window
- **Strategy backtesting** — define entry/exit conditions using RSI, SMA, EMA; backtest against historical price data
- **Live quotes** — WebSocket streaming of real-time prices (push every 5s)
- **Financial glossary** — hover tooltips explaining every metric (P/E, RSI, MACD, EPS, beta, etc.)

### Portfolio & Broker
- **Holdings management** — manual positions with quantity and average cost
- **Portfolio analytics** — allocation donut chart (by ticker/sector), portfolio value history chart, risk metrics (Sharpe ratio, alpha, beta, max drawdown, annualized volatility)
- **Portfolio performance** — P&L tracking per position, total value, cost basis, return percentage
- **CSV import/export** — import holdings from CSV, export to CSV
- **Alpaca broker sync** — import real portfolio positions from Alpaca Markets (paper or live), auto-sync on schedule
- **Paper trade execution** — place buy/sell orders through Alpaca paper trading account from the research page

### Alerts & Notifications
- **Alert center** — configurable price alerts with threshold conditions, severity levels, read/unread tracking
- **Discord notifications** — receive alert notifications via Discord webhook
- **Email notifications** — receive alert notifications via SMTP email

### UI/UX
- **Liquid Glass design** — frosted glass panels with cosmic eclipse animated background
- **Dark theme** — professional financial terminal aesthetic with cyan/green/amber/red semantic colors
- **Terminal-first** — command palette (⌘K), keyboard shortcuts, monospace financial data
- **Micro-interactions** — fade-in animations, pulsing live indicators, staggered panel entries
- **Fully responsive** — works on desktop and mobile

### Infrastructure
- **Local-first** — data stays on your machine, no cloud dependency
- **APScheduler daemon** — auto-polling quotes, news, alerts, signal outcomes, broker sync on configurable intervals
- **Provider factory** — pluggable market data, news, broker, and crypto providers
- **Alembic migrations** — versioned database schema evolution
- **Optional API key auth** — enable authentication when deploying
- **CI/CD** — GitHub Actions with backend/frontend/security checks
- **121 backend tests** — pytest, ruff, mypy
- **35 frontend tests** — vitest, testing library

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 15)                         │
│  Dashboard · Research · Compare · Screener · Portfolio          │
│  Signals · Backtest · Heatmap                                   │
│  Price Chart (Lightweight Charts) · Drawing Tools · Indicators  │
│  Factor Scores · Scenarios · Signal History · Alert Center      │
│  Macro/Markets/Sectors/Global Tabs · Trade Panel                │
│  Peer Comparison · Analyst Consensus · Dividends · Short Int.   │
│  Pattern Recognition · Earnings Summary · Glossary Tooltips     │
│  Liquid Glass UI · Cosmic Background · Animations               │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTP (localhost:8000)
┌──────────────────────▼───────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  API Routes · DB Access · Scheduler · Auth · Scoring            │
│  Strategy Backtest Engine · Pattern Detection                    │
│  DeepSeek Analysis · Provider Factory                           │
├───────────┬───────────┬────────────┬──────────┬─────────────────┤
│ SEC EDGAR │ TA-Lib    │ FRED API   │ Finnhub  │ yfinance        │
│ (XBRL)    │ (pandas-ta)│ (fredapi)  │ (news,   │ (prices+news,  │
│           │           │            │ earnings,│  ETFs, crypto)  │
│           │           │            │ analysts)│                 │
├───────────┴───────────┴────────────┴──────────┴─────────────────┤
│ CoinGecko · Alpaca (data + trading) · APScheduler               │
└─────────────────────────────────────────────────────────────────┘
```

### Pages

| Page | Route | Features |
|------|-------|----------|
| **Dashboard** | `/` | Watchlist, KPI strip, alerts, holdings, news, macro dashboard, markets overview, sector performance, ex-dividend calendar |
| **Research** | `/stocks/{symbol}` | Price chart, 30 indicators, fundamentals, AI thesis, scenarios, signal history, pattern recognition, peer comparison, analyst consensus, dividends, short interest, earnings summary, trade panel, AI explain |
| **Compare** | `/compare?tickers=AAPL,MSFT` | Side-by-side comparison of 2-5 tickers |
| **Screener** | `/screener` | 120-ticker filter with 15+ criteria, saved presets, CSV export |
| **Portfolio** | `/portfolio` | Holdings, P&L, allocation chart, value history, risk metrics |
| **Signals** | `/signals` | Signal accuracy tracking and outcome history |
| **Backtest** | `/backtest` | Strategy builder with entry/exit conditions, results dashboard |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- uv (Python package manager) — `curl -LsSf https://astral.sh/uv/install.sh | sh`

### One-time setup

```bash
git clone https://github.com/DTG404/equity-lens.git
cd equity-lens
cp .env.example .env
```

### Backend

```bash
cd backend
uv sync --group dev
uv run pytest          # 121 tests
uv run uvicorn app.main:app --reload
```

API runs on `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Database

Default is **SQLite** (zero setup). For Postgres:

```bash
docker compose up -d
# Set DATABASE_URL=postgresql://equity_lens:equity_lens@localhost:5432/equity_lens in .env
cd backend && uv run alembic upgrade head
```

### Frontend

```bash
cd frontend
npm install
npm test              # 35 tests
npm run dev           # http://localhost:3000
```

---

## Usage

### Dashboard (`/`)

![Dashboard](/screenshots/dashboard.png)

- **KPI strip** — portfolio value, signal accuracy, active alerts, market status
- **Watchlist** — add tickers, view price + change + AI signal badges, click to research
- **Macro panel** — FRED economic indicators, market indices/commodities/global, sector performance with timeframe selector
- **Alerts** — create price rules, view triggered events, mark read
- **Holdings** — manual positions with quantity and cost basis
- **News feed** — latest articles from watched tickers

### Research (`/stocks/{symbol}`)

![Research Page](/screenshots/research.png)

- **Candlestick chart** — interactive TradingView chart with volume, time range selector, drawing tools (trend lines, Fibonacci), indicator overlays, chart type toggle (line/area/bar/candlestick), RSI sub-chart
- **Fundamentals** — revenue, net income, EPS, financial statements, extended ratios (ROE, ROA, current ratio, FCF yield)
- **Technicals** — 30 indicators (RSI, MACD, Stochastic, OBV, Ichimoku, ADX, Aroon, Keltner, SuperTrend, and more)
- **Chart patterns** — auto-detected formations with confidence scores and price targets
- **Dividends** — yield, payout ratio, ex-dividend date, payment history
- **Short interest** — short float %, days to cover, squeeze potential indicator
- **Peer comparison** — ranked sector peers with percentile for each metric
- **Analyst consensus** — buy/hold/sell breakdown with price targets
- **Earnings summary** — beat/miss rate, average surprise, AI-generated earnings narrative
- **Factor scores** — technical, news sentiment, fundamentals, macro with explanations
- **AI thesis** — DeepSeek-generated analysis with bull/base/bear scenarios
- **AI explain** — beginner-friendly plain-language explanation of the analysis
- **News** — recent articles with source and relative time
- **Signal history** — past predictions and outcomes with accuracy metrics
- **Trade panel** — buy/sell quantity selector with confirmation flow (Alpaca paper trading)

### Compare (`/compare?tickers=AAPL,MSFT`)

Side-by-side comparison of 2-5 tickers on price, change, market cap, P/E, revenue growth, profit margin, RSI, and sector. Best values highlighted. URL-bookmarkable.

### Screener (`/screener`)

![Stock Screener](/screenshots/screener.png)

Filter 120 assets (stocks + ETFs) by 15+ criteria across 6 categories: valuation (P/E, P/S, P/B), financial health (D/E, profit margin, revenue growth), market metrics (market cap, beta, 52-week high), ownership (short float, institutional ownership), dividends (yield, payout ratio), and technicals (RSI, volume). Save filter presets, export results to CSV.

### Portfolio (`/portfolio`)

P&L tracking per position with total value, cost basis, and return percentage. Allocation donut chart by sector/ticker. Portfolio value history. Risk metrics: Sharpe ratio, alpha, beta, max drawdown, annualized volatility. Connect Alpaca to auto-import positions.

### Signals (`/signals`)

AI signal accuracy tracking, historical outcomes, and performance analysis by stance and timeframe.

### Backtest (`/backtest`)

Define trading strategies with entry/exit conditions (RSI, SMA, EMA thresholds). Run against historical price data. View win rate, total return, max drawdown, and comparison vs buy-and-hold.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./equity_lens.db` | Database connection string |
| `DEEPSEEK_API_KEY` | — | DeepSeek API key for AI analysis |
| `MARKET_DATA_PROVIDER` | `mock` | Market data provider (`mock`/`yfinance`) |
| `NEWS_DATA_PROVIDER` | `mock` | News provider (`mock`/`yfinance`) |
| `FRED_API_KEY` | — | FRED API key for live macro data |
| `ALPACA_API_KEY` | — | Alpaca Markets API key (for portfolio sync + paper trading) |
| `ALPACA_SECRET_KEY` | — | Alpaca Markets secret key |
| `ALPACA_PAPER` | `true` | Use Alpaca paper trading API |
| `FINNHUB_API_KEY` | — | Finnhub API key for premium news, earnings, analyst consensus |
| `DISCORD_WEBHOOK_URL` | — | Discord webhook URL for alert delivery |
| `SMTP_HOST` | — | SMTP server for email notifications |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USER` | — | SMTP username |
| `SMTP_PASSWORD` | — | SMTP password |
| `ALERT_EMAIL` | — | Recipient email for alerts |
| `API_KEY` | — | API key for endpoint authentication |
| `API_KEY_ENABLED` | `false` | Enable API key authentication |
| `QUOTE_POLL_SECONDS` | `60` | Quote polling interval |
| `NEWS_POLL_SECONDS` | `300` | News polling interval |
| `ALERT_EVAL_SECONDS` | `30` | Alert evaluation interval |
| `SIGNAL_EVAL_SECONDS` | `3600` | Signal outcome evaluation interval |
| `BROKER_SYNC_SECONDS` | `3600` | Broker sync polling interval |

---

## API Endpoints

### Public

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service health check |

### Watchlist

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/watchlist` | List watchlist with prices + AI signal badges |
| POST | `/api/watchlist` | Add ticker (auto-enriches company info) |
| DELETE | `/api/watchlist/{symbol}` | Remove ticker |

### Holdings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/holdings` | List holdings |
| POST | `/api/holdings` | Add position |
| PUT | `/api/holdings/{id}` | Update position |
| DELETE | `/api/holdings/{id}` | Remove position |

### Quotes & News

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/quotes/{symbol}` | Latest quote |
| GET | `/api/news` | Aggregated news feed |
| GET | `/api/news/{symbol}` | Per-ticker news |

### Research & Analysis

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/research/{symbol}` | Full research (quote, chart, scores, thesis, scenarios, risks) |
| POST | `/api/research/{symbol}/explain` | Beginner-friendly AI explanation |
| GET | `/api/research/{symbol}/earnings-summary` | AI earnings beat/miss analysis |
| GET | `/api/fundamentals/{symbol}` | SEC EDGAR financials + financial statements + extended ratios |
| GET | `/api/fundamentals/{symbol}/dividends` | Dividend yield, payout ratio, history |
| GET | `/api/fundamentals/{symbol}/short-interest` | Short float, days to cover, squeeze score |
| GET | `/api/technicals/{symbol}` | 30 TA-Lib indicators |
| POST | `/api/technicals/{symbol}/patterns` | Chart pattern detection |
| GET | `/api/dcf/{symbol}` | DCF valuation (fair value from SEC EDGAR fundamentals) |

### Compare & Peers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/compare?tickers=AAPL,MSFT` | Multiticker comparison (2-5 tickers) |
| GET | `/api/peers/{symbol}` | Sector peer comparison with percentiles |

### Markets & Macro

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/macro` | FRED economic dashboard (GDP, CPI, rates, unemployment) |
| GET | `/api/markets/overview` | Market indices, breadth, commodities, global |
| GET | `/api/markets/sectors?period=1d` | Sector performance by timeframe |
| GET | `/api/heatmap` | Sector heatmap (hierarchical data for treemap) |

### Filings & Ownership

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/sec/filings/{symbol}` | SEC filings browser (10-K, 10-Q, 8-K) |
| GET | `/api/sec/insider/{symbol}` | Insider trading (Form 4 transactions) |
| GET | `/api/sec/institutional/{symbol}` | Institutional ownership (13F filings) |

### Social Sentiment

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/sentiment/{symbol}` | StockTwits bullish/bearish sentiment |

### News, Earnings & Analysts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/finnhub/news/{symbol}` | Premium news via Finnhub (yfinance fallback) |
| GET | `/api/finnhub/earnings/{symbol}` | Earnings history with estimates/surprises |
| GET | `/api/finnhub/earnings-calendar` | Upcoming earnings across the market |
| GET | `/api/finnhub/analysts/{symbol}` | Analyst consensus (buy/hold/sell, price targets) |

### Screener

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/screener` | Filter stocks/ETFs by 15+ criteria |
| GET | `/api/screener/export` | Export screener results as CSV |
| POST | `/api/screener/presets` | Save filter preset |
| GET | `/api/screener/presets` | List saved presets |
| DELETE | `/api/screener/presets/{name}` | Delete preset |

### Portfolio

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/portfolio/performance` | P&L calculations per position |
| GET | `/api/portfolio/analytics` | Allocation, value history, risk metrics (Sharpe, beta, drawdown) |

### Broker & Trading

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/broker/status` | Alpaca connection status |
| POST | `/api/broker/sync` | Sync + persist broker portfolio |
| GET | `/api/broker/orders` | Order history |
| POST | `/api/broker/order` | Place buy/sell order (Alpaca paper trading) |

### CSV

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/csv/holdings` | Export holdings as CSV |
| POST | `/api/csv/holdings/import` | Import holdings from CSV file |

### Backtesting

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/backtest/signals` | Signal accuracy by stance and window |
| POST | `/api/backtest/run` | Run strategy backtest against historical data |

### Alerts

| Method | Path | Description |
|--------|------|-------------|
| GET/POST/DELETE | `/api/alerts/rules` | Alert rules CRUD |
| GET | `/api/alerts/events` | Alert events list |
| GET | `/api/alerts/events/unread-count` | Unread count |
| PATCH | `/api/alerts/events/{id}/read` | Mark event read |
| POST | `/api/alerts/events/read-all` | Mark all read |

### Notifications

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/notifications/status` | Check configured notification channels |
| POST | `/api/notifications/test` | Send test notification to all channels |

### WebSocket

| Path | Description |
|------|-------------|
| `ws://localhost:8000/ws/quotes` | Live streaming quotes (push every 5s) |

### Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/settings` | List all settings |
| GET | `/api/settings/{key}` | Get single setting |
| PUT | `/api/settings` | Upsert setting |

---

## Testing

```bash
# Backend (121 tests)
cd backend && uv run pytest

# Frontend (35 tests)
cd frontend && npm test

# Lint
cd backend && uv run ruff check app tests
cd frontend && npm run lint

# Type check
cd backend && uv run mypy app
cd frontend && npx tsc --noEmit

# Build
cd frontend && npm run build

# Secrets scan
gitleaks detect --source . --no-git

# All checks (pre-commit)
cd backend && uv run ruff check app tests && uv run mypy app && uv run pytest -x -q
cd frontend && npx tsc --noEmit && npm test && npm run build
```

---

## Project Structure

```
equity-lens/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py                # Router registration + auth
│   │   │   ├── alert_routes.py
│   │   │   ├── backtest_routes.py
│   │   │   ├── broker_routes.py
│   │   │   ├── calendar_routes.py
│   │   │   ├── compare_routes.py
│   │   │   ├── csv_routes.py
│   │   │   ├── dcf_routes.py
│   │   │   ├── finnhub_routes.py
│   │   │   ├── fundamentals_routes.py
│   │   │   ├── heatmap_routes.py
│   │   │   ├── holdings_routes.py
│   │   │   ├── macro_routes.py
│   │   │   ├── markets_routes.py
│   │   │   ├── news_routes.py
│   │   │   ├── notifications_routes.py
│   │   │   ├── pattern_routes.py
│   │   │   ├── portfolio_routes.py
│   │   │   ├── quote_routes.py
│   │   │   ├── research_routes.py
│   │   │   ├── screener_routes.py
│   │   │   ├── sec_routes.py
│   │   │   ├── settings_routes.py
│   │   │   ├── signals_routes.py
│   │   │   ├── social_routes.py
│   │   │   └── technicals_routes.py
│   │   ├── core/
│   │   │   ├── config.py                # Environment settings
│   │   │   ├── db.py                    # Async SQLAlchemy
│   │   │   ├── auth.py                  # API key auth
│   │   │   ├── scheduler.py             # APScheduler daemon
│   │   │   └── deepseek.py              # AI client
│   │   ├── domain/
│   │   │   ├── models.py                # Pydantic schemas
│   │   │   ├── db_models.py             # SQLAlchemy ORM (13+ tables)
│   │   │   ├── scoring.py               # Factor scoring engine
│   │   │   ├── technicals.py            # 30 TA-Lib indicators
│   │   │   ├── backtest.py              # Strategy backtesting engine
│   │   │   └── patterns.py              # Chart pattern detection
│   │   └── providers/
│   │       ├── base.py                  # MarketDataProvider protocol
│   │       ├── __init__.py              # Provider factory
│   │       ├── mock_market.py           # Mock data for dev/testing
│   │       ├── yfinance_provider.py
│   │       ├── news_base.py             # NewsProvider protocol
│   │       ├── yfinance_news.py
│   │       ├── sec_edgar.py             # SEC EDGAR XBRL
│   │       ├── fred.py                  # FRED economic data
│   │       ├── screener.py              # Stock + ETF screener
│   │       ├── alpaca.py                # Broker sync + trading
│   │       ├── ibkr.py                  # IBKR adapter (stub)
│   │       ├── finnhub.py               # Finnhub news/earnings/analysts
│   │       ├── markets.py               # Market indices/breadth/commodities
│   │       └── crypto.py                # CoinGecko cryptocurrency provider
│   ├── migrations/                      # Alembic migrations
│   └── tests/                           # 50+ test files (121 tests)
├── frontend/
│   ├── app/
│   │   ├── page.tsx                     # Dashboard
│   │   ├── backtest/page.tsx            # Strategy backtesting
│   │   ├── compare/page.tsx             # Multiticker comparison
│   │   ├── portfolio/page.tsx           # Portfolio + analytics
│   │   ├── research/page.tsx            # Research launcher
│   │   ├── screener/page.tsx            # Stock screener
│   │   ├── signals/page.tsx             # Signal history
│   │   └── stocks/[symbol]/page.tsx     # Research page
│   └── src/
│       ├── lib/
│       │   ├── api.ts                   # API client (all endpoints)
│       │   └── glossary.ts              # Financial metric definitions
│       └── components/
│           ├── AllocationChart.tsx       # Portfolio allocation donut
│           ├── AnalystConsensus.tsx      # Analyst ratings panel
│           ├── BacktestBuilder.tsx       # Strategy builder form
│           ├── BacktestResults.tsx       # Backtest results dashboard
│           ├── ChartTypeSelector.tsx     # Candlestick/line/area/bar toggle
│           ├── CompareTable.tsx          # Side-by-side comparison table
│           ├── DashboardShell.tsx        # Main dashboard
│           ├── DividendPanel.tsx         # Dividend data display
│           ├── EarningsSummary.tsx       # AI earnings analysis
│           ├── ExplainPanel.tsx          # AI explain feature
│           ├── FactorScoreCard.tsx       # Score bars
│           ├── IndicatorOverlay.tsx      # Technical indicator toggle
│           ├── KpiStrip.tsx              # KPI cards
│           ├── MacroPanel.tsx            # Macro/Markets/Sectors/Global tabs
│           ├── MetricTooltip.tsx         # Glossary hover tooltips
│           ├── NavBar.tsx                # Glass navigation
│           ├── PatternPanel.tsx          # Chart pattern display
│           ├── PeerComparisonPanel.tsx   # Sector peer comparison
│           ├── PortfolioValueChart.tsx   # Portfolio value history
│           ├── PriceChart.tsx            # Enhanced price chart
│           ├── RiskMetricCard.tsx        # Sharpe/alpha/beta/drawdown
│           ├── ScenarioCard.tsx          # Bull/base/bear scenarios
│           ├── ShortInterestPanel.tsx    # Short interest display
│           ├── SignalHistory.tsx         # Signal table
│           ├── StatusBar.tsx             # Terminal footer
│           ├── SubChart.tsx              # RSI/MACD sub-charts
│           └── TradePanel.tsx            # Buy/sell order panel
├── docker-compose.yml
├── AGENTS.md
└── .env.example
```

---

## Migrations

```bash
cd backend
uv run alembic revision --autogenerate -m "description"  # Create migration
uv run alembic upgrade head                               # Apply
uv run alembic downgrade -1                               # Rollback
uv run alembic check                                      # Check for drift
uv run alembic history                                    # View history
```

---

## Safety

- **Not financial advice.** All analysis is for informational and research purposes only.
- **Paper trading only.** Trade execution uses Alpaca paper trading accounts. No real money is ever moved.
- **Uncertainty is shown.** Every prediction displays confidence scores and model used.
- **Full audit trail.** Every analysis stores input data, model, timestamp, and output.
- **Local-first.** Data stays on your machine. No cloud dependency.
- **Auth optional.** API key authentication available when deploying.

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Alembic |
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS v4 |
| Charts | TradingView Lightweight Charts, d3.js (heatmap) |
| Database | SQLite or Postgres 16 via Alembic |
| Fundamentals | SEC EDGAR XBRL (free) |
| Technicals | TA-Lib / pandas-ta (30+ indicators) |
| Macro | FRED API (free, 120 req/min) |
| Market data | yfinance (stocks, ETFs, crypto) |
| Crypto | CoinGecko API (free, no key) |
| News & Analysts | Finnhub API |
| AI | DeepSeek V4 (fallback without API key) |
| Broker | Alpaca Markets REST API (data + paper trading) |
| Scheduler | APScheduler (AsyncIO) |
| Auth | FastAPI APIKeyHeader (optional) |
| Testing | pytest, ruff, mypy, Vitest, Testing Library |
| CI/CD | GitHub Actions (Backend CI, Frontend CI, Security Scan) |
| Security | gitleaks |

---

## License

MIT © DTG404
