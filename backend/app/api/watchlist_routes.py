"""Watchlist CRUD endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import PriceSnapshot, WatchlistEntry
from app.domain.models import TickerSymbol

router = APIRouter(prefix='/watchlist', tags=['watchlist'])


class WatchlistCreateRequest(BaseModel):
    symbol: str
    company_name: str = ''

    @field_validator('symbol')
    @classmethod
    def validate_and_uppercase(cls, v: str) -> str:
        TickerSymbol(value=v)
        return v.upper()


@router.get('')
async def list_watchlist(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    result = await session.execute(select(WatchlistEntry).order_by(WatchlistEntry.created_at))
    entries = result.scalars().all()
    output = []
    for entry in entries:
        snapshot = await session.execute(
            select(PriceSnapshot)
            .where(PriceSnapshot.symbol == entry.symbol)
            .order_by(PriceSnapshot.recorded_at.desc())
            .limit(1)
        )
        price = snapshot.scalar_one_or_none()
        output.append({
            'symbol': entry.symbol,
            'company_name': entry.company_name,
            'price': price.price if price else None,
            'change_percent': price.change_percent if price else None,
        })
    return output


@router.post('')
async def add_to_watchlist(
    body: WatchlistCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    existing = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == body.symbol)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail=f'{body.symbol} already in watchlist')

    entry = WatchlistEntry(symbol=body.symbol, company_name=body.company_name)
    session.add(entry)
    await session.flush()
    return {'symbol': entry.symbol, 'company_name': entry.company_name}


@router.delete('/{symbol}')
async def remove_from_watchlist(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == symbol.upper())
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail=f'{symbol.upper()} not in watchlist')
    await session.delete(entry)
    return {'status': 'removed', 'symbol': symbol.upper()}
