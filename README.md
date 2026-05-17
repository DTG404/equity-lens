# Equity Lens

> Local-first personal stock research terminal.

Equity Lens is a local-first application for researching US equities. It combines real-time market data, financial news intelligence, AI-powered analysis, and signal tracking into a single dashboard. It is not a trading platform — it does not execute trades, connect to brokerage APIs, or provide financial advice.

---

## Features

- **Watchlist management** — add/remove US stock tickers to track prices and news
- **Manual holdings** — track portfolio positions with quantity and cost basis
- **Live pricing** — configurable quote polling via yfinance with watchlist price display
- **Financial news** — per-ticker news ingestion with deduplication and relative timestamps
- **Single-stock research pages** — deep dives with price chart, news, factor analysis, AI thesis, and risk assessment
- **AI-powered predictions** — data-driven factor scoring with DeepSeek-generated scenarios
- **Bull/base/bear scenarios** — structured scenario analysis for every prediction
- **Analysis audit trail** — every prediction is stored with full input snapshots, model metadata, and timestamps
- **Alert center** — configurable price alerts with threshold conditions, severity levels, read/unread tracking
- **Signal outcome tracking** — 1d/1w/1m accuracy measurement against actual price movements
- **Settings store** — persistent key-value configuration
- **Safety framing** — uncertainty shown on every prediction, evidence cited, personal-use disclaimer

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Frontend (Next.js)              │
│  Dashboard · Research Page · Alert Center   │
│  Signal History · Price Chart · Scenarios   │
└──────────────────┬──────────────────────────┘
                   │ HTTP (localhost:8000)
┌──────────────────▼──────────────────────────┐
│             Backend (FastAPI)                │
│  API Routes · DB Access · Scheduler         │
│  Factor Scoring · DeepSeek Analysis          │
└──────┬──────────────┬──────────────┬─────────┘
       │              │              │
       ▼              ▼              ▼
┌──────────┐  ┌────────────┐  ┌──────────┐
│ Postgres │  │ yfinance   │  │ DeepSeek │
│ (Docker) │  │ (market +  │  │ API (AI  │
│          │  │  news)     │  │ analysis)│
└──────────┘  └────────────┘  └──────────┘
```

### Layers

| Layer | Technology | Responsibility |
|-------|-----------|----------------|
| **Frontend** | Next.js 15, TypeScript, React 19, Vitest | Dashboard UI, research pages, alert center, charts |
| **Backend API** | Python FastAPI, Pydantic v2, SQLAlchemy 2.0 async | CRUD endpoints, business logic, data aggregation |
| **Database** | Postgres 16 (Docker) or SQLite (dev) | Watchlists, holdings, price snapshots, news, analyses, alerts, signal outcomes, settings |
| **Market provider** | yfinance (pluggable via protocol) | Real-time quotes, price history |
| **News provider** | yfinance ticker news (pluggable via protocol) | Per-ticker financial news |
| **AI provider** | DeepSeek API (pluggable) | Thesis generation, scenario analysis |
| **Background workers** | Python async scheduler | Quote polling, news ingestion, alert evaluation, signal outcome measurement |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for Postgres) or use SQLite for local dev
- uv (Python package manager) — `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`

### One-time setup

```bash
# Clone and enter
git clone https://github.com/digitalghost404/equity-lens.git
cd equity-lens

# Copy environment config
cp .env.example .env
# Optionally set DEEPSEEK_API_KEY for AI-powered analysis
```

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Run tests (82+ tests)
uv run pytest

# Start the API server
uv run uvicorn app.main:app --reload
```

The backend runs on `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

### Database

By default, Equity Lens uses **SQLite** (`./equity_lens.db`), which requires no setup.

To use Postgres instead:

```bash
# Start Postgres
docker compose up -d

# Set DATABASE_URL in .env
# DATABASE_URL=postgresql://equity_lens:equity_lens@localhost:5432/equity_lens
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run tests (38+ tests)
npm test -- --run

# Start dev server
npm run dev
```

The frontend runs on `http://localhost:3000`.

---

## Usage

### 1. Dashboard (`/`)

The main dashboard shows:

- **Watchlist** — add tickers via the text input, view current price and change percent, click a symbol to open the research page
- **Holdings** — enter manual portfolio positions with quantity and average cost
- **Alert Center** — create price rules (above/below thresholds), view triggered alerts with severity levels, mark events as read
- **News Feed** — recent financial news aggregated from watched tickers

### 2. Research Page (`/stocks/{symbol}`)

Click any watchlist symbol to open the research page:

- **Price summary** — latest price, change percent, provider info
- **Price chart** — SVG line chart of recent close prices (30 days)
- **Factor scores** — technical, news sentiment, fundamentals, macro with explanations
- **AI Thesis** — generated analysis with DeepSeek (or fallback if no API key configured)
- **Scenarios** — bull, base, and bear cases with structured analysis
- **News** — recent articles relevant to this ticker
- **Signal history** — past predictions and their outcomes for this ticker
- **Risks** — key risk factors

### 3. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service health check |
| GET/POST/DELETE | `/api/watchlist` | Watchlist CRUD |
| GET/POST/PUT/DELETE | `/api/holdings` | Holdings CRUD |
| GET/PUT | `/api/settings` | Key-value settings |
| GET | `/api/quotes/{symbol}` | Latest quote |
| GET | `/api/news` | Aggregated news feed |
| GET | `/api/news/{symbol}` | Per-ticker news |
| GET | `/api/research/{symbol}` | Full research aggregation (quote, history, news, scores, thesis, scenarios, risks) |
| GET/POST/DELETE | `/api/alerts/rules` | Alert rules CRUD |
| GET/PATCH/POST | `/api/alerts/events` | Alert events (list, mark read, mark all read) |
| GET | `/api/alerts/events/unread-count` | Unread alert count |
| GET | `/api/signals/outcomes` | Signal outcome history |
| GET | `/api/signals/metrics` | Accuracy metrics |

---

## Configuration

| Environment Variable | Default | Description |
|--------------------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./equity_lens.db` | Database connection string |
| `DEEPSEEK_API_KEY` | (empty) | DeepSeek API key for AI analysis |
| `MARKET_DATA_PROVIDER` | `mock` | Market data provider (mock/yfinance) |
| `NEWS_DATA_PROVIDER` | `mock` | News provider (mock/yfinance) |
| `QUOTE_POLL_SECONDS` | `60` | Quote polling interval |

---

## Testing

```bash
# Backend (82+ tests)
cd backend && uv run pytest

# Frontend (38+ tests)
cd frontend && npm test -- --run

# Lint
cd backend && uv run ruff check app tests
cd frontend && npm run lint

# Type check
cd backend && uv run mypy app

# Build
cd frontend && npm run build

# Secrets scan
gitleaks detect --source . --no-git --config .gitleaks.toml
```

---

## Project Structure

```
equity-lens/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route handlers
│   │   │   ├── routes.py  # Router registration
│   │   │   ├── watchlist_routes.py
│   │   │   ├── holdings_routes.py
│   │   │   ├── settings_routes.py
│   │   │   ├── quote_routes.py
│   │   │   ├── news_routes.py
│   │   │   ├── research_routes.py
│   │   │   ├── alert_routes.py
│   │   │   └── signals_routes.py
│   │   ├── core/          # Configuration, DB, scheduler, AI
│   │   │   ├── config.py  # Environment-based settings
│   │   │   ├── db.py      # Async SQLAlchemy engine + session
│   │   │   ├── scheduler.py  # Background workers
│   │   │   └── deepseek.py   # DeepSeek API client
│   │   ├── domain/        # Pydantic schemas + ORM models
│   │   │   ├── models.py  # Pydantic domain models
│   │   │   ├── db_models.py  # SQLAlchemy ORM models
│   │   │   └── scoring.py    # Factor scoring engine
│   │   └── providers/     # Pluggable data providers
│   │       ├── base.py         # MarketDataProvider protocol
│   │       ├── mock_market.py  # Mock provider for testing
│   │       ├── yfinance_provider.py  # Real market data
│   │       ├── news_base.py    # NewsProvider protocol
│   │       └── yfinance_news.py    # Real news data
│   └── tests/             # 16 test files (82+ tests)
├── frontend/
│   ├── app/               # Next.js App Router pages
│   │   ├── page.tsx       # Dashboard
│   │   └── stocks/[symbol]/page.tsx  # Research page
│   └── src/
│       ├── lib/api.ts     # API client
│       └── components/    # React components
│           ├── DashboardShell.tsx
│           ├── AlertCenter.tsx
│           ├── PriceChart.tsx
│           ├── FactorScoreCard.tsx
│           ├── ScenarioCard.tsx
│           └── SignalHistory.tsx
├── docker-compose.yml     # Postgres 16
├── AGENTS.md              # Agent workflow commands
└── .env.example           # Environment template
```

---

## Safety

- **Not financial advice.** All analysis is for informational and research purposes only.
- **No trade execution.** Equity Lens cannot place trades or connect to brokerage accounts.
- **Uncertainty is shown.** Every prediction displays confidence scores and clearly identifies the model that generated it (including fallback text when no AI API key is configured).
- **Full audit trail.** Every analysis stores the input data, model used, timestamp, and generated output for review.
- **Local-first.** Data stays on your machine. API keys are stored in backend-local environment variables, not exposed to the frontend.

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Alembic |
| Frontend | Next.js 15, TypeScript, React 19, Vitest, Testing Library |
| Database | Postgres 16 (Docker) or SQLite (dev) |
| Market data | yfinance (pluggable provider interface) |
| AI | DeepSeek V4 (pluggable, graceful fallback without API key) |
| Testing | pytest, ruff, mypy, Vitest, tsc |
| Security | gitleaks |

---

## License

MIT © digitalghost404
