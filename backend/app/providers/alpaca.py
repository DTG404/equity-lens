"""Alpaca Markets broker integration for portfolio sync."""

import httpx

from app.core.config import settings
from app.providers.base import BrokerPosition, BrokerSyncResult

ALPACA_PAPER_URL = 'https://paper-api.alpaca.markets'
ALPACA_LIVE_URL = 'https://api.alpaca.markets'


def _get_base_url() -> str:
    return ALPACA_PAPER_URL if settings.alpaca_paper else ALPACA_LIVE_URL


def _get_headers() -> dict[str, str]:
    return {
        'APCA-API-KEY-ID': settings.alpaca_api_key,
        'APCA-API-SECRET-KEY': settings.alpaca_secret_key,
    }


class AlpacaBrokerProvider:
    """Broker provider that syncs portfolio data from Alpaca Markets."""

    provider_name = 'alpaca'

    def __init__(self) -> None:
        self._base_url = _get_base_url()
        self._headers = _get_headers()

    def is_configured(self) -> bool:
        """Check if Alpaca credentials are configured."""
        return bool(settings.alpaca_api_key and settings.alpaca_secret_key)

    async def sync_portfolio(self) -> BrokerSyncResult:
        """Fetch current positions from Alpaca and return them."""
        if not self.is_configured():
            return BrokerSyncResult(
                positions=[],
                portfolio_value=0.0,
                cash=0.0,
                equity=0.0,
                position_count=0,
                provider='alpaca',
                error='Alpaca not configured',
            )

        async with httpx.AsyncClient() as client:
            account_resp = await client.get(
                f'{self._base_url}/v2/account',
                headers=self._headers,
                timeout=10,
            )
            if account_resp.status_code == 401:
                return BrokerSyncResult(
                    positions=[],
                    portfolio_value=0.0,
                    cash=0.0,
                    equity=0.0,
                    position_count=0,
                    provider='alpaca',
                    error='Invalid Alpaca credentials',
                )
            account_resp.raise_for_status()
            account = account_resp.json()

            positions_resp = await client.get(
                f'{self._base_url}/v2/positions',
                headers=self._headers,
                timeout=10,
            )
            positions_resp.raise_for_status()
            positions = positions_resp.json()

        portfolio_value = float(account.get('portfolio_value', 0))
        cash = float(account.get('cash', 0))

        synced = []
        for pos in positions:
            qty = float(pos.get('qty', 0))
            cost_basis = float(pos.get('cost_basis', 0))
            market_value = float(pos.get('market_value', 0))
            avg_entry = float(pos.get('avg_entry_price', 0))
            current = float(pos.get('current_price', 0))
            change = ((current - avg_entry) / avg_entry * 100) if avg_entry else 0

            synced.append(BrokerPosition(
                symbol=pos.get('symbol'),
                quantity=qty,
                avg_cost=round(avg_entry, 2),
                current_price=round(current, 2),
                market_value=round(market_value, 2),
                cost_basis=round(cost_basis, 2),
                pl_pct=round(change, 2),
            ))

        return BrokerSyncResult(
            positions=synced,
            portfolio_value=round(portfolio_value, 2),
            cash=round(cash, 2),
            equity=round(float(account.get('equity', 0)), 2),
            position_count=len(synced),
            provider='alpaca',
            account_id=account.get('id', ''),
        )
