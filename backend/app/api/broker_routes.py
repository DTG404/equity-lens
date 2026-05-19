"""Broker sync and order placement API."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import Holding, Order
from app.providers import get_broker_provider
from app.providers.base import BrokerProvider

router = APIRouter(prefix='/broker', tags=['broker'])


class OrderRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    side: str = Field(..., pattern=r'^(buy|sell)$')
    quantity: float = Field(..., gt=0)
    order_type: str = Field('market', pattern=r'^(market|limit|stop|stop_limit)$')
    time_in_force: str = Field('day', pattern=r'^(day|gtc|ioc|fok)$')


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


async def place_alpaca_order(
    symbol: str, side: str, qty: float,
    order_type: str = 'market', tif: str = 'day',
) -> dict[str, Any]:
    """Place an order via Alpaca paper trading API."""
    provider = get_broker_provider()
    if not provider.is_configured():
        return {'error': 'Alpaca not configured', 'order_id': ''}

    from app.providers.alpaca import _get_base_url, _get_headers

    base_url = _get_base_url()
    headers = _get_headers()

    import httpx
    payload = {
        'symbol': symbol,
        'qty': str(qty),
        'side': side,
        'type': order_type,
        'time_in_force': tif,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f'{base_url}/v2/orders', json=payload, headers=headers, timeout=10)
        if response.status_code == 403:
            return {'error': 'Alpaca trading not enabled for this account', 'order_id': ''}
        if response.status_code == 422:
            data = response.json()
            return {'error': data.get('message', 'Invalid order'), 'order_id': ''}
        response.raise_for_status()
        data = response.json()

    return {
        'order_id': data.get('id', ''),
        'symbol': data.get('symbol', ''),
        'filled_qty': float(data.get('filled_qty', 0) or 0),
        'filled_avg_price': float(data.get('filled_avg_price', 0) or 0),
        'status': data.get('status', 'unknown'),
    }


@router.post('/order')
async def create_order(body: OrderRequest, session: AsyncSession = Depends(get_session)) -> dict[str, Any]:
    """Place a buy/sell order via Alpaca paper trading."""
    order = Order(
        symbol=body.symbol.upper(),
        side=body.side,
        quantity=body.quantity,
        order_type=body.order_type,
        time_in_force=body.time_in_force,
    )
    session.add(order)
    await session.flush()

    result = await place_alpaca_order(order.symbol, order.side, order.quantity, order.order_type, order.time_in_force)

    if 'error' in result:
        order.status = 'rejected'
    else:
        order.status = result.get('status', 'pending')
        order.order_id = result.get('order_id', '')
        order.filled_qty = result.get('filled_qty', 0)
        order.filled_price = result.get('filled_avg_price', 0)

    await session.commit()

    return {
        'id': order.id,
        'symbol': order.symbol,
        'side': order.side,
        'quantity': order.quantity,
        'status': order.status,
        'order_id': order.order_id,
        'filled_qty': order.filled_qty,
        'filled_price': order.filled_price,
    }


@router.get('/orders')
async def get_orders(session: AsyncSession = Depends(get_session)) -> list[dict[str, Any]]:
    """Return order history."""
    result = await session.execute(select(Order).order_by(desc(Order.created_at)).limit(50))
    orders = result.scalars().all()
    return [
        {
            'id': o.id,
            'symbol': o.symbol,
            'side': o.side,
            'quantity': o.quantity,
            'order_type': o.order_type,
            'status': o.status,
            'filled_qty': o.filled_qty,
            'filled_price': o.filled_price,
            'order_id': o.order_id,
            'created_at': o.created_at.isoformat() if o.created_at else '',
        }
        for o in orders
    ]
