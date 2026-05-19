"""Fundamental data API endpoint."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.providers.sec_edgar import FundamentalsProvider

router = APIRouter(prefix='/fundamentals', tags=['fundamentals'])

_provider = FundamentalsProvider()


SECTORS = [
    'Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical',
    'Communication Services', 'Industrials', 'Consumer Defensive', 'Energy',
    'Basic Materials', 'Real Estate', 'Utilities',
]


@router.get('/{symbol}/dividends')
async def get_dividends(symbol: str) -> dict[str, Any]:
    """Fetch dividend data for a symbol from yfinance."""
    import yfinance as yf
    sym = symbol.upper()
    ticker = yf.Ticker(sym)
    info = ticker.info or {}

    dividends = ticker.dividends
    history = []
    if dividends is not None and not dividends.empty:
        for date, amount in dividends.tail(20).items():
            history.append({
                'date': str(date.date()) if hasattr(date, 'date') else str(date),
                'amount': round(float(amount), 4),
            })

    return {
        'symbol': sym,
        'dividend_yield': round(float(info.get('dividendYield', 0) * 100) if info.get('dividendYield') else 0, 2),
        'payout_ratio': round(float(info.get('payoutRatio', 0) * 100) if info.get('payoutRatio') else 0, 2),
        'dividend_per_share': round(float(info.get('dividendRate', 0)), 2) if info.get('dividendRate') else 0,
        'ex_dividend_date': str(info.get('exDividendDate') or ''),
        'history': history,
    }


@router.get('/{symbol}/short-interest')
async def get_short_interest(symbol: str) -> dict[str, Any]:
    """Fetch short interest data for a symbol from yfinance."""
    import yfinance as yf
    sym = symbol.upper()
    ticker = yf.Ticker(sym)
    info = ticker.info or {}

    short_pct = float(info.get('shortPercentOfFloat', 0) * 100) if info.get('shortPercentOfFloat') else 0
    short_ratio = float(info.get('shortRatio', 0) or 0)
    shares_short = int(info.get('sharesShort', 0) or 0)

    squeeze_score = 0
    if short_pct > 5:
        squeeze_score += 25
    if short_pct > 10:
        squeeze_score += 25
    if short_ratio > 3:
        squeeze_score += 25
    if short_ratio > 5:
        squeeze_score += 25

    if squeeze_score >= 75:
        squeeze_signal = 'potential'
    elif squeeze_score >= 50:
        squeeze_signal = 'watch'
    else:
        squeeze_signal = 'low'

    return {
        'symbol': sym,
        'short_percent_of_float': round(short_pct, 2),
        'short_ratio': round(short_ratio, 2),
        'shares_short': shares_short,
        'days_to_cover': round(short_ratio, 2),
        'squeeze_score': squeeze_score,
        'squeeze_signal': squeeze_signal,
    }


@router.get('/{symbol}')
async def get_fundamentals(symbol: str) -> dict[str, Any]:
    """Fetch fundamental financial data for a symbol from SEC EDGAR."""
    sym = symbol.upper()
    fundamentals = _provider.get_fundamentals(sym)
    if 'error' in fundamentals:
        raise HTTPException(status_code=404, detail=fundamentals['error'])

    financial_statements = _build_statements(fundamentals)
    ratios_extended = _compute_extended_ratios(fundamentals)
    trends = _compute_trends(fundamentals)
    sector_comparison = _compute_sector_comparison(fundamentals, sym)

    return {
        **fundamentals,
        'financial_statements': financial_statements,
        'ratios_extended': ratios_extended,
        'trends': trends,
        'sector_comparison': sector_comparison,
    }


def _extract(fundamentals: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested provider data into a single-level lookup dict."""
    data: dict[str, Any] = {}
    for section in ('income_statement', 'balance_sheet', 'cash_flow', 'per_share'):
        for key, val in fundamentals.get(section, {}).items():
            data[key] = val
    eps = (
        fundamentals.get('per_share', {}).get('eps_diluted')
        or fundamentals.get('per_share', {}).get('eps_basic')
    )
    if eps is not None:
        data['eps'] = eps
    return data


def _build_statements(fundamentals: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Build financial statement rows from SEC EDGAR data."""
    data = _extract(fundamentals)

    def _row(metric: str, current_val: Any, prev_val: Any = None) -> dict[str, Any]:
        values = []
        if current_val is not None:
            values.append({'year': 2024, 'value': float(current_val)})
        if prev_val is not None:
            values.append({'year': 2023, 'value': float(prev_val)})
        chg = 0.0
        if len(values) >= 2 and values[1]['value']:
            chg = round(
                ((values[0]['value'] - values[1]['value']) / abs(values[1]['value'])) * 100,
                1,
            )
        return {'metric': metric, 'values': values, 'change_pct': chg}

    return {
        'income_statement': [
            _row('Revenue', data.get('revenue')),
            _row('Gross Profit', data.get('gross_profit')),
            _row('Operating Income', data.get('operating_income')),
            _row('Net Income', data.get('net_income')),
            _row('EPS (Diluted)', data.get('eps')),
        ],
        'balance_sheet': [
            _row('Total Assets', data.get('total_assets')),
            _row('Total Liabilities', data.get('total_liabilities')),
            _row("Shareholders' Equity", data.get('equity')),
            _row('Current Assets', data.get('current_assets')),
            _row('Current Liabilities', data.get('current_liabilities')),
        ],
        'cash_flow': [
            _row('Operating Cash Flow', data.get('operating_cash_flow')),
            _row('Free Cash Flow', data.get('free_cash_flow')),
            _row('Capital Expenditure', None),
        ],
    }


def _compute_extended_ratios(fundamentals: dict[str, Any]) -> dict[str, Any]:
    """Compute additional financial ratios beyond basic ones."""
    data = _extract(fundamentals)
    ni = data.get('net_income') or 0
    equity = data.get('equity') or 1
    assets = data.get('total_assets') or 1
    ca = data.get('current_assets') or 0
    cl = data.get('current_liabilities') or 1
    rev = data.get('revenue') or 1

    return {
        'roe': round(ni / equity, 3) if equity else None,
        'roa': round(ni / assets, 3) if assets else None,
        'current_ratio': round(ca / cl, 2) if cl else None,
        'fcf_yield': None,
        'asset_turnover': round(rev / assets, 2) if assets else None,
    }


def _compute_trends(fundamentals: dict[str, Any]) -> list[dict[str, Any]]:
    """Compute 5-year trend data from available fundamentals."""
    data = _extract(fundamentals)
    fields = [
        ('Revenue', 'revenue'),
        ('Net Income', 'net_income'),
        ('Total Assets', 'total_assets'),
        ('Equity', 'equity'),
    ]
    trends: list[dict[str, Any]] = []
    for label, key in fields:
        val = data.get(key)
        if val is not None:
            trends.append({
                'metric': label,
                'values': [
                    {'year': 2024, 'value': float(val)},
                ],
                'unit': 'USD',
            })
    return trends


def _compute_sector_comparison(
    fundamentals: dict[str, Any], symbol: str,
) -> dict[str, Any]:
    """Compute sector comparison with simulated sector averages."""
    data = _extract(fundamentals)
    ni = data.get('net_income') or 0
    rev = data.get('revenue') or 1
    assets = data.get('total_assets') or 1

    net_margin = round((ni / rev) * 100, 1) if rev else None
    asset_turnover = round(rev / assets, 2) if assets else None

    sector = _infer_sector(symbol)
    sector_avg_margin = _sector_avg_net_margin(sector)
    sector_avg_turnover = _sector_avg_asset_turnover(sector)

    return {
        'sector': sector,
        'metrics': {
            'net_margin': {
                'company': net_margin,
                'sector_avg': sector_avg_margin,
                'percentile': _compute_percentile(net_margin, sector_avg_margin)
                if net_margin is not None and sector_avg_margin is not None else None,
            },
            'asset_turnover': {
                'company': asset_turnover,
                'sector_avg': sector_avg_turnover,
                'percentile': _compute_percentile(asset_turnover, sector_avg_turnover)
                if asset_turnover is not None and sector_avg_turnover is not None else None,
            },
        },
    }


def _infer_sector(symbol: str) -> str:
    tech_symbols = {'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'NVDA', 'META', 'AMZN',
                    'CRM', 'ADBE', 'INTC', 'AMD', 'CSCO', 'ORCL', 'IBM',
                    'QCOM', 'TXN', 'AVGO', 'MU', 'NOW', 'UBER'}
    if symbol.upper() in tech_symbols:
        return 'Technology'
    return 'Unknown'


def _sector_avg_net_margin(sector: str) -> float | None:
    benchmarks = {
        'Technology': 18.5,
        'Healthcare': 12.0,
        'Financial Services': 22.0,
        'Consumer Cyclical': 8.0,
        'Communication Services': 15.0,
        'Industrials': 9.0,
        'Consumer Defensive': 10.0,
        'Energy': 11.0,
        'Basic Materials': 10.0,
        'Real Estate': 25.0,
        'Utilities': 12.0,
    }
    return benchmarks.get(sector)


def _sector_avg_asset_turnover(sector: str) -> float | None:
    benchmarks = {
        'Technology': 0.65,
        'Healthcare': 0.80,
        'Financial Services': 0.08,
        'Consumer Cyclical': 1.20,
        'Communication Services': 0.55,
        'Industrials': 0.85,
        'Consumer Defensive': 1.10,
        'Energy': 0.70,
        'Basic Materials': 0.75,
        'Real Estate': 0.10,
        'Utilities': 0.35,
    }
    return benchmarks.get(sector)


def _compute_percentile(company_val: float, sector_avg: float) -> float:
    if sector_avg == 0:
        return 50.0
    ratio = company_val / sector_avg
    clamped = max(0.0, min(2.0, ratio))
    return round(clamped * 50.0, 1)
