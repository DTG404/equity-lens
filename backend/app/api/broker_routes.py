"""Broker sync API endpoint."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import Holding
from app.providers import get_broker_provider
from app.providers.base import BrokerProvider

router = APIRouter(prefix='/broker', tags=['broker'])


@router.get('/status')
async def get_broker_status() -> dict[str, Any]:
    """Check if Alpaca is configured."""
    provider = get_broker_provider()
    return {
        'configured': provider.is_configured(),
        'provider': provider.provider_name,
    }


async def sync_and_persist(
    provider: BrokerProvider | None = None,
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """Sync from broker and persist to Holdings table."""
    if provider is None:
        provider = get_broker_provider()
    if not provider.is_configured():
        return {'status': 'not_configured', 'provider': provider.provider_name}

    data = await provider.sync_portfolio()
    if data.error:
        return {'status': 'error', 'error': data.error, 'provider': provider.provider_name}

    if session is None:
        raise ValueError('session required')

    synced_symbols: set[str] = set()
    for pos in data.positions:
        synced_symbols.add(pos.symbol)
        existing = await session.execute(
            select(Holding).where(Holding.symbol == pos.symbol)
        )
        holding = existing.scalar_one_or_none()
        if holding:
            holding.quantity = pos.quantity
            holding.average_cost = pos.avg_cost
        else:
            session.add(Holding(
                symbol=pos.symbol,
                quantity=pos.quantity,
                average_cost=pos.avg_cost,
            ))

    all_holdings = await session.execute(select(Holding))
    for h in all_holdings.scalars().all():
        if h.symbol not in synced_symbols:
            await session.delete(h)

    await session.commit()

    return {
        'status': 'ok',
        'provider': data.provider,
        'positions_synced': len(data.positions),
        'portfolio_value': data.portfolio_value,
        'cash': data.cash,
        'equity': data.equity,
    }


@router.post('/sync')
async def sync_from_broker(
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Sync portfolio positions from Alpaca and persist to Holdings table."""
    result = await sync_and_persist(session=session)
    if result['status'] == 'not_configured':
        raise HTTPException(status_code=400, detail='Alpaca not configured')
    if result['status'] == 'error':
        raise HTTPException(status_code=401, detail=result.get('error', 'Sync failed'))
    return result
