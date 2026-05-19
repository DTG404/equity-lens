"""Stock screener — filters a predefined universe by user criteria."""

import asyncio
from typing import Any

import yfinance as yf

from app.domain.technicals import compute_technicals
from app.providers.sec_edgar import FundamentalsProvider

# Predefined universe of popular stocks (S&P 500 top components + common tickers)
UNIVERSE = [
    'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'AVGO', 'BRK.B', 'JPM',
    'V', 'JNJ', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'NFLX', 'ADBE',
    'CRM', 'PYPL', 'INTC', 'AMD', 'QCOM', 'TXN', 'BA', 'NKE', 'COST', 'CVX',
    'ABT', 'MRK', 'PEP', 'KO', 'PFE', 'TMO', 'ACN', 'DHR', 'LIN', 'NEE',
    'T', 'IBM', 'HON', 'UPS', 'RTX', 'SPGI', 'LOW', 'GS', 'MS', 'C',
    'BLK', 'SCHW', 'AXP', 'SYK', 'BSX', 'CAT', 'DE', 'GE', 'LMT', 'MMM',
    'SBUX', 'MCD', 'BKNG', 'UBER', 'ABNB', 'AMAT', 'ADI', 'PANW', 'CRWD', 'SNPS',
    'REGN', 'VRTX', 'GILD', 'AMGN', 'ISRG', 'MDT', 'SYY', 'ZTS', 'CL', 'TGT',
]

ETF_UNIVERSE = [
    'SPY', 'QQQ', 'IVV', 'VTI', 'VOO', 'IWM', 'VXUS', 'BND', 'AGG', 'GLD',
    'SLV', 'TLT', 'IEF', 'LQD', 'HYG', 'EEM', 'VWO', 'XLF', 'XLK', 'XLV',
    'XLE', 'XLI', 'XLB', 'XLRE', 'XLU', 'XLP', 'XLY', 'XLC', 'ARKK', 'ARKG',
    'QCLN', 'TAN', 'ICLN', 'LABU', 'SOXX', 'SMH', 'IBIT', 'FBTC', 'BITO', 'USO', 'UNG',
]

ALL_SYMBOLS = [*UNIVERSE, *ETF_UNIVERSE]
ETF_SET = frozenset(ETF_UNIVERSE)

_fundamentals_provider = FundamentalsProvider()


async def screen_stocks(
    price_min: float | None = None,
    price_max: float | None = None,
    sector: str | None = None,
    rsi_min: float | None = None,
    rsi_max: float | None = None,
    volume_min: int | None = None,
    # Valuation
    pe_min: float | None = None,
    pe_max: float | None = None,
    ps_min: float | None = None,
    ps_max: float | None = None,
    pb_min: float | None = None,
    pb_max: float | None = None,
    # Financial health
    max_debt_to_equity: float | None = None,
    min_profit_margin: float | None = None,
    min_revenue_growth: float | None = None,
    # Market metrics
    market_cap_min: float | None = None,
    market_cap_max: float | None = None,
    beta_min: float | None = None,
    beta_max: float | None = None,
    # Ownership
    short_float_min: float | None = None,
    short_float_max: float | None = None,
    min_inst_ownership: float | None = None,
    # Dividends
    dividend_yield_min: float | None = None,
    dividend_yield_max: float | None = None,
    # Asset type & ETF filters
    asset_type: str = '',
    expense_ratio_min: float | None = None,
    expense_ratio_max: float | None = None,
    sort_by: str = 'symbol',
    sort_dir: str = 'asc',
    limit: int = 50,
    skip: int = 0,
) -> dict[str, Any]:
    """Screen the stock universe by the given criteria."""
    results: list[dict[str, Any]] = []
    errors: int = 0

    def fetch_stock(symbol: str) -> dict[str, Any] | None:
        """Fetch stock info (runs in thread pool to avoid blocking)."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
            vol = info.get('volume') or 0
            name = info.get('longName') or info.get('shortName') or symbol
            change = info.get('regularMarketChangePercent') or 0
            return {
                'symbol': symbol,
                'info': info,
                'price': price,
                'vol': vol,
                'name': name,
                'change': change,
            }
        except Exception:
            return None

    # Fetch all stocks and ETFs concurrently using thread pool
    tasks = [asyncio.to_thread(fetch_stock, symbol) for symbol in ALL_SYMBOLS]
    stock_data = await asyncio.gather(*tasks)

    for data in stock_data:
        if data is None:
            errors += 1
            continue

        symbol = data['symbol']
        info = data['info']
        price = data['price']
        vol = data['vol']

        # Apply price filter
        if price_min is not None and price < price_min:
            continue
        if price_max is not None and price > price_max:
            continue

        # Apply volume filter
        if volume_min is not None and vol < volume_min:
            continue

        # Apply sector filter
        if sector and sector.lower() not in (info.get('sector') or '').lower():
            continue

        # Extract new metric values (may be None if yfinance doesn't have them)
        market_cap = info.get('marketCap')
        pe = info.get('trailingPE')
        ps = info.get('priceToSalesTrailingMonths')
        pb = info.get('priceToBook')
        debt_to_equity = info.get('debtToEquity')
        profit_margin = info.get('profitMargins')
        revenue_growth = info.get('revenueGrowth')
        beta = info.get('beta')
        short_float = info.get('shortPercentOfFloat')
        inst_ownership = info.get('heldPercentInstitutions')
        dividend_yield = info.get('dividendYield')

        # Apply valuation filters
        if pe_min is not None and (pe is None or pe < pe_min):
            continue
        if pe_max is not None and (pe is None or pe > pe_max):
            continue
        if ps_min is not None and (ps is None or ps < ps_min):
            continue
        if ps_max is not None and (ps is None or ps > ps_max):
            continue
        if pb_min is not None and (pb is None or pb < pb_min):
            continue
        if pb_max is not None and (pb is None or pb > pb_max):
            continue

        # Apply financial health filters
        if max_debt_to_equity is not None and (debt_to_equity is None or debt_to_equity > max_debt_to_equity):
            continue
        if min_profit_margin is not None and (profit_margin is None or profit_margin < min_profit_margin):
            continue
        if min_revenue_growth is not None and (revenue_growth is None or revenue_growth < min_revenue_growth):
            continue

        # Apply market metric filters
        if market_cap_min is not None and (market_cap is None or market_cap < market_cap_min):
            continue
        if market_cap_max is not None and (market_cap is None or market_cap > market_cap_max):
            continue
        if beta_min is not None and (beta is None or beta < beta_min):
            continue
        if beta_max is not None and (beta is None or beta > beta_max):
            continue

        # Apply ownership filters
        if short_float_min is not None and (short_float is None or short_float < short_float_min):
            continue
        if short_float_max is not None and (short_float is None or short_float > short_float_max):
            continue
        if min_inst_ownership is not None and (inst_ownership is None or inst_ownership < min_inst_ownership):
            continue

        # Apply dividend filters
        if dividend_yield_min is not None and (dividend_yield is None or dividend_yield < dividend_yield_min):
            continue
        if dividend_yield_max is not None and (dividend_yield is None or dividend_yield > dividend_yield_max):
            continue

        # Determine asset type and extract expense ratio
        sym_asset_type = 'etf' if symbol in ETF_SET else 'stock'
        expense_ratio = info.get('expenseRatio') if sym_asset_type == 'etf' else None

        # Apply asset type filter
        if asset_type and sym_asset_type != asset_type:
            continue

        # Apply expense ratio filter (only meaningful for ETFs)
        if expense_ratio is not None:
            if expense_ratio_min is not None and expense_ratio < expense_ratio_min:
                continue
            if expense_ratio_max is not None and expense_ratio > expense_ratio_max:
                continue

        # Get technicals for RSI filter (only if needed)
        rsi = None
        if rsi_min is not None or rsi_max is not None:
            try:
                tech = await compute_technicals(symbol)
                if 'error' not in tech:
                    rsi = tech.get('rsi')
            except Exception:
                pass

        # Apply RSI filter
        if rsi_min is not None and (rsi is None or rsi < rsi_min):
            continue
        if rsi_max is not None and (rsi is None or rsi > rsi_max):
            continue

        results.append({
            'symbol': symbol,
            'name': data['name'],
            'price': round(float(price), 2),
            'change_percent': round(float(data['change']), 2),
            'volume': int(vol),
            'sector': info.get('sector') or '',
            'market_cap': market_cap,
            'pe_ratio': pe,
            'ps_ratio': ps,
            'pb_ratio': pb,
            'debt_to_equity': debt_to_equity,
            'profit_margin': profit_margin,
            'revenue_growth': revenue_growth,
            'beta': beta,
            'short_float': short_float,
            'inst_ownership': inst_ownership,
            'dividend_yield': dividend_yield,
            'rsi': round(rsi, 1) if rsi is not None else None,
            'asset_type': sym_asset_type,
            'expense_ratio': round(float(expense_ratio), 4) if expense_ratio is not None else None,
        })

    # Sort
    reverse = sort_dir.lower() == 'desc'
    valid_keys = {
        'symbol', 'price', 'change_percent', 'volume', 'market_cap', 'pe_ratio',
        'ps_ratio', 'pb_ratio', 'debt_to_equity', 'profit_margin',
        'revenue_growth', 'beta', 'short_float', 'inst_ownership',
        'dividend_yield', 'rsi', 'asset_type', 'expense_ratio',
    }
    if sort_by in valid_keys:
        results.sort(key=lambda x: (x.get(sort_by) is None, x.get(sort_by) or 0), reverse=reverse)

    total = len(results)

    # Paginate
    paged = results[skip:skip + limit]

    return {
        'total': total,
        'returned': len(paged),
        'errors': errors,
        'results': paged,
    }
