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

_fundamentals_provider = FundamentalsProvider()


async def screen_stocks(
    price_min: float | None = None,
    price_max: float | None = None,
    sector: str | None = None,
    rsi_min: float | None = None,
    rsi_max: float | None = None,
    volume_min: int | None = None,
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

    # Fetch all stocks concurrently using thread pool
    tasks = [asyncio.to_thread(fetch_stock, symbol) for symbol in UNIVERSE]
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
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'rsi': round(rsi, 1) if rsi is not None else None,
        })

    # Sort
    reverse = sort_dir.lower() == 'desc'
    valid_keys = {'symbol', 'price', 'change_percent', 'volume', 'market_cap', 'pe_ratio', 'rsi'}
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
