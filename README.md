# Equity Lens

> AI-native, local-first stock research terminal.

Equity Lens is a futuristic financial research terminal with a liquid glass UI, AI-powered analysis, and local-first architecture. It combines real-time market data, SEC EDGAR fundamentals, TA-Lib technical indicators, FRED macroeconomic data, news intelligence, and DeepSeek-generated thesis analysis into a single desktop application. It does not execute trades or provide financial advice.

---

## Features

### Data & Analysis
- **Watchlist management** — add/remove US stock tickers with live price tracking and AI signal badges
- **SEC EDGAR fundamentals** — revenue, net income, EPS, balance sheet, ratios, free cash flow (free, audit-quality)
- **SEC filings browser** — view recent 10-K, 10-Q, 8-K filings in-app
- **Insider trading** — monitor Form 4 insider transactions per ticker
- **Institutional ownership** — track 13F filing data per ticker
- **DCF valuation** — automated fair value estimates from SEC EDGAR fundamentals
- **TA-Lib technical indicators** — RSI, MACD, SMA/EMA, Bollinger Bands, ATR
- **FRED macroeconomic dashboard** — GDP, CPI, unemployment, Fed funds rate, Treasury yields, consumer sentiment
- **Social sentiment** — StockTwits bullish/bearish sentiment overlay
- **Stock screener** — 80-ticker universe filtered by price, sector, RSI, volume, with sortable results
- **Premium news** — Finnhub news provider with yfinance fallback
- **Earnings calendar** — upcoming earnings dates with consensus estimates
- **AI-powered analysis** — DeepSeek-generated thesis with bull/base/bear scenarios and factor scoring
- **Price chart** — interactive candlestick chart with volume histogram (TradingView Lightweight Charts)
- **Per-ticker news** — deduplicated financial news with sentiment scoring
- **Signal tracking** — 1d/1w/1m accuracy measurement with outcome logging
- **Signal backtesting** — aggregate accuracy and returns by stance and time window
- **Live quotes** — WebSocket streaming of real-time prices (push every 5s)

### Portfolio & Broker
- **Holdings management** — manual positions with quantity and average cost
- **Portfolio performance** — P&L tracking per position, total value, cost basis, return percentage
- **CSV import/export** — import holdings from CSV, export to CSV
- **Alpaca broker sync** — import real portfolio positions from Alpaca Markets (paper or live)

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
- **APScheduler daemon** — auto-polling quotes, news, alerts, signal outcomes on configurable intervals
- **Provider factory** — pluggable market data and news providers (mock/yfinance)
- **Alembic migrations** — versioned database schema evolution
- **Optional API key auth** — enable authentication when deploying
- **CI/CD** — GitHub Actions with backend/frontend/security checks
- **87 backend tests** — pytest, ruff, mypy
- **35 frontend tests** — vitest, testing library

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 15)                        │
│  Dashboard · Research Page · Screener · Portfolio · Signals    │
│  Price Chart (Lightweight Charts) · Factor Scores · Scenarios  │
│  Signal History · Alert Center · Macro Panel · KPI Strip      │
│  Liquid Glass UI · Cosmic Background · Animations             │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP (localhost:8000)
┌─────────────────────▼───────────────────────────────────────────┐
│                    Backend (FastAPI)                            │
│  API Routes · DB Access · Scheduler · Auth · Scoring           │
│  DeepSeek Analysis · Provider Factory                           │
├────────────┬───────────┬────────────┬───────────┬──────────────┤
│ SEC EDGAR  │ TA-Lib    │ FRED API   │ Alpaca    │ yfinance     │
│ (XBRL)     │ (pandas-ta)│ (fredapi)  │ (REST)   │ (prices+news)│
└────────────┴───────────┴────────────┴───────────┴──────────────┘
```

### Layers

| Layer | Technology | Responsibility |
|-------|-----------|----------------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS v4 | Dashboard UI, research pages, screener, portfolio, signals, charts |
| **Backend API** | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 | CRUD endpoints, business logic, data aggregation, auth |
| **Database** | SQLite (dev) or Postgres 16 (Docker) via Alembic | Watchlists, holdings, price data, news, analyses, alerts, signals, settings |
| **Fundamentals** | SEC EDGAR XBRL (free) | Income statement, balance sheet, cash flow, ratios |
| **Technicals** | TA-Lib / pandas-ta | RSI, MACD, SMA/EMA, Bollinger Bands, ATR |
| **Macro** | FRED API (free, 120 req/min) | GDP, CPI, unemployment, rates, sentiment |
| **Market data** | yfinance (pluggable via protocol) | Real-time quotes, price history |
| **News** | yfinance ticker news (pluggable) | Per-ticker financial news |
| **AI** | DeepSeek API (pluggable, graceful fallback) | Thesis generation, scenario analysis |
| **Broker** | Alpaca Markets API | Portfolio sync, position import |
| **Auth** | API key header (optional) | X-API-Key verification |
| **Background** | APScheduler (AsyncIO) | Quote/news polling, alert evaluation, signal tracking |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- uv (Python package manager) — `curl -LsSf https://astral.sh/uv/install.sh | sh`

### One-time setup

```bash
git clone https://github.com/digitalghost404/equity-lens.git
cd equity-lens
cp .env.example .env
```

### Backend

```bash
cd backend
uv sync --group dev
uv run pytest          # 87 tests
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
- **Alerts** — create price rules, view triggered events, mark read
- **Holdings** — manual positions with quantity and cost basis
- **News feed** — latest articles from watched tickers
- **Macro dashboard** — 9 economic indicators (GDP, CPI, rates, unemployment)

### Research (`/stocks/{symbol}`)

![Research Page](/screenshots/research.png)

- **Candlestick chart** — interactive TradingView chart with volume, time range selector
- **Fundamentals** — revenue, net income, EPS, D/E ratio, margins from SEC EDGAR
- **Technicals** — RSI, MACD, SMA/EMA, Bollinger Bands
- **Factor scores** — technical, news sentiment, fundamentals, macro with explanations
- **AI thesis** — DeepSeek-generated analysis with bull/base/bear scenarios
- **News** — recent articles with source and relative time
- **Signal history** — past predictions and outcomes with accuracy metrics

### Screener (`/screener`)

![Stock Screener](/screenshots/screener.png)

Filter 80 popular stocks by price range, sector, RSI, and volume. Sortable columns with links to research pages.

### Portfolio (`/portfolio`)

P&L tracking per position with total value, cost basis, and return percentage. Connect Alpaca to auto-import positions.

### Signals (`/signals`)

AI signal accuracy tracking, historical outcomes, and performance analysis by stance and timeframe.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./equity_lens.db` | Database connection string |
| `DEEPSEEK_API_KEY` | — | DeepSeek API key for AI analysis |
| `MARKET_DATA_PROVIDER` | `mock` | Market data provider (`mock`/`yfinance`) |
| `NEWS_DATA_PROVIDER` | `mock` | News provider (`mock`/`yfinance`) |
| `FRED_API_KEY` | — | FRED API key for live macro data |
| `ALPACA_API_KEY` | — | Alpaca Markets API key |
| `ALPACA_SECRET_KEY` | — | Alpaca Markets secret key |
| `ALPACA_PAPER` | `true` | Use Alpaca paper trading API |
| `FINNHUB_API_KEY` | — | Finnhub API key for news & earnings |
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
| GET | `/api/fundamentals/{symbol}` | SEC EDGAR financials (revenue, net income, EPS, ratios) |
| GET | `/api/technicals/{symbol}` | TA-Lib indicators (RSI, MACD, SMA, Bollinger, ATR) |
| GET | `/api/macro` | FRED economic dashboard (GDP, CPI, rates, unemployment) |
| GET | `/api/dcf/{symbol}` | DCF valuation (fair value from SEC EDGAR fundamentals) |

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

### News & Earnings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/finnhub/news/{symbol}` | Premium news via Finnhub (yfinance fallback) |
| GET | `/api/finnhub/earnings/{symbol}` | Earnings history with estimates/surprises |
| GET | `/api/finnhub/earnings-calendar` | Upcoming earnings across the market |

### Alerts

| Method | Path | Description |
|--------|------|-------------|
| GET/POST/DELETE | `/api/alerts/rules` | Alert rules CRUD |
| GET | `/api/alerts/events` | Alert events list |
| GET | `/api/alerts/events/unread-count` | Unread count |
| PATCH | `/api/alerts/events/{id}/read` | Mark event read |
| POST | `/api/alerts/events/read-all` | Mark all read |

### Signals

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/signals/outcomes` | Signal outcomes (pagination) |
| GET | `/api/signals/metrics` | Accuracy metrics |

### Screener

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/screener` | Filter stocks by price, sector, RSI, volume |

### Portfolio & Broker

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/portfolio/performance` | P&L calculations per position |
| GET | `/api/broker/status` | Alpaca connection status |
| POST | `/api/broker/sync` | Import positions from Alpaca |
| GET | `/api/csv/holdings` | Export holdings as CSV |
| POST | `/api/csv/holdings/import` | Import holdings from CSV file |

### Backtesting & Signals

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/backtest/signals` | Signal accuracy by stance and window |

### Notifications

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/notifications/status` | Check configured notification channels |
| POST | `/api/notifications/test` | Send test notification to all channels |

### WebSocket

| Path | Description |
|------|-------------|
| `ws://localhost:8000/ws/quotes` | Live streaming quotes (push every 5s) |

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/settings` | List all settings |
| GET | `/api/settings/{key}` | Get single setting |
| PUT | `/api/settings` | Upsert setting |

---

## Testing

```bash
# Backend (87 tests)
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
│   │   │   ├── routes.py          # Router registration + auth
│   │   │   ├── watchlist_routes.py
│   │   │   ├── holdings_routes.py
│   │   │   ├── settings_routes.py
│   │   │   ├── quote_routes.py
│   │   │   ├── news_routes.py
│   │   │   ├── research_routes.py
│   │   │   ├── alert_routes.py
│   │   │   ├── signals_routes.py
│   │   │   ├── fundamentals_routes.py
│   │   │   ├── technicals_routes.py
│   │   │   ├── macro_routes.py
│   │   │   ├── screener_routes.py
│   │   │   ├── portfolio_routes.py
│   │   │   └── broker_routes.py
│   │   ├── core/
│   │   │   ├── config.py          # Environment settings
│   │   │   ├── db.py              # Async SQLAlchemy
│   │   │   ├── auth.py            # API key auth
│   │   │   ├── scheduler.py       # APScheduler daemon
│   │   │   └── deepseek.py        # AI client
│   │   ├── domain/
│   │   │   ├── models.py          # Pydantic schemas
│   │   │   ├── db_models.py       # SQLAlchemy ORM (12 tables)
│   │   │   ├── scoring.py         # Factor scoring engine
│   │   │   └── technicals.py      # TA-Lib computations
│   │   └── providers/
│   │       ├── base.py            # MarketDataProvider protocol
│   │       ├── __init__.py        # Provider factory
│   │       ├── mock_market.py     # Mock data for dev/testing
│   │       ├── yfinance_provider.py
│   │       ├── news_base.py       # NewsProvider protocol
│   │       ├── yfinance_news.py
│   │       ├── sec_edgar.py       # SEC EDGAR XBRL
│   │       ├── fred.py            # FRED economic data
│   │       ├── screener.py        # Stock screener engine
│   │       └── alpaca.py          # Broker sync
│   ├── migrations/                # Alembic migrations
│   └── tests/                     # 28 test files (87 tests)
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Dashboard
│   │   ├── research/page.tsx      # Research launcher
│   │   ├── screener/page.tsx      # Stock screener
│   │   ├── signals/page.tsx       # Signal history
│   │   ├── portfolio/page.tsx     # Portfolio performance
│   │   └── stocks/[symbol]/page.tsx  # Research page
│   └── src/
│       ├── lib/api.ts             # API client
│       └── components/
│           ├── DashboardShell.tsx  # Main dashboard
│           ├── NavBar.tsx          # Glass navigation
│           ├── KpiStrip.tsx        # KPI cards
│           ├── StatusBar.tsx       # Terminal footer
│           ├── AlertCenter.tsx     # Alert management
│           ├── PriceChart.tsx      # Lightweight Charts
│           ├── FactorScoreCard.tsx # Score bars
│           ├── ScenarioCard.tsx    # Bull/base/bear
│           ├── SignalHistory.tsx   # Signal table
│           ├── MacroPanel.tsx      # FRED dashboard
│           └── ResearchPanels.tsx  # Fundamentals + Technicals
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
- **No trade execution.** Equity Lens cannot place trades.
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
| Charts | TradingView Lightweight Charts |
| Database | SQLite or Postgres 16 via Alembic |
| Fundamentals | SEC EDGAR XBRL (free) |
| Technicals | TA-Lib / pandas-ta |
| Macro | FRED API (free, 120 req/min) |
| Market data | yfinance |
| AI | DeepSeek V4 (fallback without API key) |
| Broker | Alpaca Markets REST API |
| Scheduler | APScheduler (AsyncIO) |
| Auth | FastAPI APIKeyHeader (optional) |
| Testing | pytest, ruff, mypy, Vitest, Testing Library |
| CI/CD | GitHub Actions (Backend CI, Frontend CI, Security Scan) |
| Security | gitleaks |

---

## License

MIT © digitalghost404
