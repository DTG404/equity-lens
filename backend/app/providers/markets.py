"""Market indices, breadth, commodities, and global data provider."""

from typing import Any


async def get_markets_overview() -> dict[str, Any]:
    """Fetch market indices, breadth, commodities, and global data."""
    import yfinance as yf

    indices_symbols = {
        '^GSPC': 'S&P 500',
        '^IXIC': 'NASDAQ',
        '^DJI': 'Dow Jones',
        '^VIX': 'VIX',
    }
    commodity_symbols = {
        'GC=F': 'Gold',
        'CL=F': 'Crude Oil',
        'HG=F': 'Copper',
    }
    global_symbols = {
        '^FTSE': 'FTSE 100',
        '^N225': 'Nikkei 225',
        '^GDAXI': 'DAX',
    }

    def _fetch_quotes(symbols: dict[str, str]) -> list[dict[str, Any]]:
        results = []
        for sym, name in symbols.items():
            try:
                ticker = yf.Ticker(sym)
                info = ticker.info or {}
                price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                prev_close = info.get('previousClose') or price or 1
                change_pct = round(((price - prev_close) / prev_close) * 100, 2) if prev_close else 0
                results.append({
                    'symbol': sym,
                    'name': name,
                    'price': round(float(price), 2) if price else 0,
                    'change_pct': change_pct,
                })
            except Exception:
                pass
        return results

    indices = _fetch_quotes(indices_symbols)
    commodities = _fetch_quotes(commodity_symbols)
    global_data = _fetch_quotes(global_symbols)

    # Market breadth from S&P 500 data
    breadth = None
    try:
        sp = yf.Ticker('^GSPC')
        sp_info = sp.info or {}
        breadth = {
            'advancers': sp_info.get('advancers', 0),
            'decliners': sp_info.get('decliners', 0),
            'advance_decline_ratio': round(
                sp_info.get('advancers', 0) / max(sp_info.get('decliners', 1), 1), 2
            ),
            'new_highs': sp_info.get('newHighs', 0),
            'new_lows': sp_info.get('newLows', 0),
        }
    except Exception:
        breadth = None

    return {
        'indices': indices,
        'breadth': breadth,
        'commodities': commodities,
        'global': global_data,
    }
