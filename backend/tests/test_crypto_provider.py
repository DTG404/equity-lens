"""Tests for CoinGecko crypto provider."""

import re

import pytest
import respx
from httpx import Response

from app.providers.crypto import COINGECKO_BASE, get_crypto_history, get_crypto_quote


@pytest.fixture(autouse=True)
def _mock_coingecko(respx_mock: respx.MockRouter) -> None:
    """Mock CoinGecko API to avoid rate limiting (free tier: ~10 req/min)."""
    respx_mock.get(url=re.compile(rf'{re.escape(COINGECKO_BASE)}/simple/price.*')).mock(
        Response(200, json={
            'bitcoin': {
                'usd': 50000,
                'usd_24h_change': 2.5,
                'usd_market_cap': 1_000_000_000_000,
                'usd_24h_vol': 50_000_000_000,
            },
        }),
    )
    respx_mock.get(url=re.compile(rf'{re.escape(COINGECKO_BASE)}/coins/bitcoin/ohlc.*')).mock(
        Response(200, json=[[1_700_000_000, 48000, 51000, 47000, 50000]]),
    )


@pytest.mark.asyncio
async def test_crypto_quote_returns_btc_data() -> None:
    result = await get_crypto_quote('BTC')
    assert 'error' not in result
    assert result['symbol'] == 'BTC'
    assert result['price'] > 0
    assert result['provider'] == 'coingecko'


@pytest.mark.asyncio
async def test_crypto_quote_unknown_symbol() -> None:
    result = await get_crypto_quote('ZZZCOIN')
    assert 'error' in result


@pytest.mark.asyncio
async def test_crypto_history_returns_ohlcv() -> None:
    result = await get_crypto_history('BTC', days=7)
    assert len(result) > 0
    assert 'date' in result[0]
    assert 'close' in result[0]


@pytest.mark.asyncio
async def test_crypto_quote_caches_results() -> None:
    result1 = await get_crypto_quote('BTC')
    result2 = await get_crypto_quote('BTC')
    assert result1['symbol'] == result2['symbol'] == 'BTC'
