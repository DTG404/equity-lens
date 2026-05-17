"""Holdings CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import Holding
from app.domain.models import TickerSymbol

router = APIRouter(prefix='/holdings', tags=['holdings'])


class HoldingCreateRequest(BaseModel):
    symbol: str
    quantity: float
    average_cost: float
    notes: str = ''

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        TickerSymbol(value=v)
        return v.upper()


class HoldingUpdateRequest(BaseModel):
    quantity: float
    average_cost: float
    notes: str = ''


@router.get('')
async def list_holdings(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, object]]:
    result = await session.execute(select(Holding).order_by(Holding.created_at))
    holdings = result.scalars().all()
    return [
        {
            'id': h.id,
            'symbol': h.symbol,
            'quantity': h.quantity,
            'average_cost': h.average_cost,
            'notes': h.notes,
        }
        for h in holdings
    ]


@router.post('')
async def add_holding(
    body: HoldingCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    holding = Holding(
        symbol=body.symbol,
        quantity=body.quantity,
        average_cost=body.average_cost,
        notes=body.notes,
    )
    session.add(holding)
    await session.flush()
    return {
        'id': holding.id,
        'symbol': holding.symbol,
        'quantity': holding.quantity,
        'average_cost': holding.average_cost,
        'notes': holding.notes,
    }


@router.put('/{holding_id}')
async def update_holding(
    holding_id: int,
    body: HoldingUpdateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    result = await session.execute(select(Holding).where(Holding.id == holding_id))
    holding = result.scalar_one_or_none()
    if holding is None:
        raise HTTPException(status_code=404, detail='Holding not found')

    holding.quantity = body.quantity
    holding.average_cost = body.average_cost
    holding.notes = body.notes
    await session.flush()
    return {
        'id': holding.id,
        'symbol': holding.symbol,
        'quantity': holding.quantity,
        'average_cost': holding.average_cost,
        'notes': holding.notes,
    }


@router.delete('/{holding_id}')
async def delete_holding(
    holding_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(select(Holding).where(Holding.id == holding_id))
    holding = result.scalar_one_or_none()
    if holding is None:
        raise HTTPException(status_code=404, detail='Holding not found')
    await session.delete(holding)
    return {'status': 'deleted', 'id': str(holding_id)}
