"""Tests for broker sync protocol."""

import httpx
import pytest

from app.providers.base import (
    BrokerPosition,
    BrokerProvider,
    BrokerSyncResult,
)


class FakeBroker:
    provider_name = 'mock'

    def is_configured(self) -> bool:
        return True

    async def sync_portfolio(self) -> BrokerSyncResult:
        return BrokerSyncResult(
            positions=[],
            portfolio_value=0,
            cash=0,
            equity=0,
            position_count=0,
            provider='mock',
        )


def test_broker_protocol_structural_subtyping() -> None:
    """Classes implementing the protocol should pass isinstance checks."""
    assert isinstance(FakeBroker(), BrokerProvider)


def test_broker_position_dataclass() -> None:
    pos = BrokerPosition(
        symbol='AAPL',
        quantity=10,
        avg_cost=150.0,
        current_price=180.0,
        market_value=1800.0,
        cost_basis=1500.0,
        pl_pct=20.0,
    )
    assert pos.symbol == 'AAPL'
    assert pos.quantity == 10
    assert pos.avg_cost == 150.0
    assert pos.current_price == 180.0
    assert pos.market_value == 1800.0
    assert pos.cost_basis == 1500.0
    assert pos.pl_pct == 20.0


def test_broker_sync_result() -> None:
    result = BrokerSyncResult(
        positions=[],
        portfolio_value=0.0,
        cash=0.0,
        equity=0.0,
        position_count=0,
        provider='alpaca',
    )
    assert result.provider == 'alpaca'
    assert result.position_count == 0
    assert result.portfolio_value == 0.0
    assert result.cash == 0.0
    assert result.equity == 0.0
    assert result.positions == []
    # Verify default values
    assert result.account_id == ''
    assert result.error == ''


@pytest.mark.asyncio
async def test_alpaca_implements_broker_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """AlpacaBrokerProvider should implement BrokerProvider protocol."""
    monkeypatch.setattr('app.core.config.settings.alpaca_api_key', 'test_key')
    monkeypatch.setattr('app.core.config.settings.alpaca_secret_key', 'test_secret')

    from app.providers.alpaca import AlpacaBrokerProvider

    provider = AlpacaBrokerProvider()
    assert isinstance(provider, BrokerProvider)
    assert provider.provider_name == 'alpaca'
    assert provider.is_configured() is True

    # Mock HTTP calls to return empty data
    async def mock_get(self: object, url: str, *args: object, **kwargs: object) -> object:
        class MockResponse:
            status_code = 200

            def json(self) -> dict[str, object] | list[object]:
                if 'v2/account' in str(url):
                    return {
                        'id': 'test123',
                        'portfolio_value': '10000',
                        'cash': '5000',
                        'equity': '15000',
                    }
                return []

            def raise_for_status(self) -> None:
                pass

        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_get)

    result = await provider.sync_portfolio()
    assert isinstance(result, BrokerSyncResult)
    assert result.provider == 'alpaca'
    assert result.portfolio_value == 10000.0
    assert result.position_count == 0


@pytest.mark.asyncio
async def test_ibkr_stub_returns_not_configured() -> None:
    from app.providers.ibkr import IBKRBrokerProvider

    provider = IBKRBrokerProvider()
    assert provider.provider_name == 'ibkr'
    assert provider.is_configured() is False

    result = await provider.sync_portfolio()
    assert result.error == 'IBKR not configured'
    assert result.position_count == 0


@pytest.mark.asyncio
async def test_sync_persists_holdings(async_db_session, monkeypatch) -> None:
    from sqlalchemy import select

    from app.api.broker_routes import sync_and_persist
    from app.domain.db_models import Holding
    from app.providers.base import BrokerPosition, BrokerSyncResult

    class MockBroker:
        provider_name = 'mock'
        def is_configured(self) -> bool:
            return True
        async def sync_portfolio(self) -> BrokerSyncResult:
            return BrokerSyncResult(
                positions=[BrokerPosition(
                    symbol='AAPL', quantity=10, avg_cost=150.0,
                    current_price=180.0, market_value=1800.0,
                    cost_basis=1500.0, pl_pct=20.0,
                )],
                portfolio_value=1800.0, cash=500.0, equity=2300.0,
                position_count=1, provider='mock',
            )

    result = await sync_and_persist(MockBroker(), async_db_session)
    assert result['positions_synced'] == 1

    db_result = await async_db_session.execute(
        select(Holding).where(Holding.symbol == 'AAPL')
    )
    holding = db_result.scalar_one_or_none()
    assert holding is not None
    assert holding.quantity == 10
    assert holding.average_cost == 150.0


@pytest.mark.asyncio
async def test_sync_removes_stale_holdings(
    async_db_session,
    monkeypatch,
) -> None:
    from sqlalchemy import select

    from app.api.broker_routes import sync_and_persist
    from app.domain.db_models import Holding
    from app.providers.base import BrokerPosition, BrokerSyncResult

    async_db_session.add(Holding(symbol='STALE', quantity=1, average_cost=100.0))
    await async_db_session.commit()

    class MockBroker:
        provider_name = 'mock'
        def is_configured(self) -> bool:
            return True
        async def sync_portfolio(self) -> BrokerSyncResult:
            return BrokerSyncResult(
                positions=[BrokerPosition(
                    symbol='AAPL', quantity=10, avg_cost=150.0,
                    current_price=180.0, market_value=1800.0,
                    cost_basis=1500.0, pl_pct=20.0,
                )],
                portfolio_value=1800.0, cash=500.0, equity=2300.0,
                position_count=1, provider='mock',
            )

    await sync_and_persist(MockBroker(), async_db_session)

    stale = await async_db_session.execute(
        select(Holding).where(Holding.symbol == 'STALE')
    )
    assert stale.scalar_one_or_none() is None
