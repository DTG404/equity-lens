"""IBKR (Interactive Brokers) broker adapter stub.

This adapter is a placeholder for when the user sets up an IBKR account.
It implements the BrokerProvider protocol but always returns 'not configured'.
"""

from app.providers.base import BrokerSyncResult


class IBKRBrokerProvider:
    provider_name = 'ibkr'

    def is_configured(self) -> bool:
        return False

    async def sync_portfolio(self) -> BrokerSyncResult:
        return BrokerSyncResult(
            positions=[],
            portfolio_value=0,
            cash=0,
            equity=0,
            position_count=0,
            provider='ibkr',
            error='IBKR not configured',
        )
