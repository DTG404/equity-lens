"""Cryptocurrency data provider using CoinGecko API (free, no key needed)."""

import time
from typing import Any, cast

import httpx

COINGECKO_BASE = 'https://api.coingecko.com/api/v3'
COINGECKO_IDS = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
    'XRP': 'ripple', 'ADA': 'cardano', 'DOT': 'polkadot',
    'LINK': 'chainlink', 'AVAX': 'avalanche-2', 'MATIC': 'matic-network',
    'DOGE': 'dogecoin',
}

_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL = 60  # seconds


def _get_cached(key: str) -> Any | None:
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return val
    return None


def _set_cache(key: str, val: Any) -> None:
    _cache[key] = (time.time(), val)


async def get_crypto_quote(symbol: str) -> dict[str, Any]:
    """Fetch current price and market data for a cryptocurrency."""
    sym = symbol.upper()
    coin_id = COINGECKO_IDS.get(sym)
    if not coin_id:
        return {'error': f'Unknown crypto symbol: {sym}'}

    cached = _get_cached(f'quote_{sym}')
    if cached:
        return cast(dict[str, Any], cached)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'{COINGECKO_BASE}/simple/price',
            params={
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
            },
            timeout=10,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json().get(coin_id, {})

    result = {
        'symbol': sym,
        'price': data.get('usd', 0),
        'change_24h_pct': round(float(data.get('usd_24h_change', 0)), 2),
        'market_cap': data.get('usd_market_cap', 0),
        'volume_24h': data.get('usd_24h_vol', 0),
        'provider': 'coingecko',
    }
    _set_cache(f'quote_{sym}', result)
    return result


async def get_crypto_history(symbol: str, days: int = 30) -> list[dict[str, Any]]:
    """Fetch OHLCV price history for a cryptocurrency."""
    sym = symbol.upper()
    coin_id = COINGECKO_IDS.get(sym)
    if not coin_id:
        return []

    cached = _get_cached(f'hist_{sym}_{days}')
    if cached:
        return cast(list[dict[str, Any]], cached)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'{COINGECKO_BASE}/coins/{coin_id}/ohlc',
            params={'vs_currency': 'usd', 'days': days},
            timeout=10,
        )
        response.raise_for_status()
        data: list[Any] = response.json()

    history = []
    for item in data:
        timestamp, open_p, high, low, close = item[:5]
        history.append({
            'date': str(timestamp),
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
        })
    _set_cache(f'hist_{sym}_{days}', history)
    return history
