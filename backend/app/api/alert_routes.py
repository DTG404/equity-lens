"""Alert rule and event API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import AlertEvent, AlertRule

router = APIRouter(prefix='/alerts', tags=['alerts'])

VALID_ALERT_TYPES = {'price', 'news', 'signal', 'risk'}
VALID_CONDITIONS = {'above', 'below'}


class CreateRuleRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    alert_type: str
    condition: str = 'above'
    threshold: float = 0.0


@router.get('/rules')
async def list_rules(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, object]]:
    result = await session.execute(select(AlertRule).order_by(AlertRule.id))
    rules = result.scalars().all()
    return [
        {
            'id': r.id,
            'symbol': r.symbol,
            'alert_type': r.alert_type,
            'condition': r.condition,
            'threshold': r.threshold,
            'enabled': r.enabled,
            'created_at': r.created_at.isoformat() if r.created_at else '',
        }
        for r in rules
    ]


@router.post('/rules')
async def create_rule(
    body: CreateRuleRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    if body.alert_type not in VALID_ALERT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f'alert_type must be one of: {", ".join(sorted(VALID_ALERT_TYPES))}',
        )
    if body.condition not in VALID_CONDITIONS:
        raise HTTPException(
            status_code=422,
            detail=f'condition must be one of: {", ".join(sorted(VALID_CONDITIONS))}',
        )

    rule = AlertRule(
        symbol=body.symbol.upper(),
        alert_type=body.alert_type,
        condition=body.condition,
        threshold=body.threshold,
    )
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return {
        'id': rule.id,
        'symbol': rule.symbol,
        'alert_type': rule.alert_type,
        'condition': rule.condition,
        'threshold': rule.threshold,
        'enabled': rule.enabled,
        'created_at': rule.created_at.isoformat() if rule.created_at else '',
    }


@router.delete('/rules/{rule_id}')
async def delete_rule(
    rule_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(
        select(AlertRule).where(AlertRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=404, detail='Rule not found')
    await session.delete(rule)
    await session.commit()
    return {'status': 'deleted'}


@router.get('/events')
async def list_events(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, object]]:
    result = await session.execute(
        select(AlertEvent)
        .order_by(AlertEvent.triggered_at.desc())
        .limit(50)
    )
    events = result.scalars().all()
    return [
        {
            'id': e.id,
            'symbol': e.symbol,
            'alert_type': e.alert_type,
            'message': e.message,
            'severity': e.severity,
            'read': e.read,
            'triggered_at': e.triggered_at.isoformat() if e.triggered_at else '',
        }
        for e in events
    ]


@router.get('/events/unread-count')
async def unread_count(
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    result = await session.execute(
        select(AlertEvent).where(AlertEvent.read.is_(False))
    )
    count = len(result.scalars().all())
    return {'count': count}


@router.patch('/events/{event_id}/read')
async def mark_event_read(
    event_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(
        select(AlertEvent).where(AlertEvent.id == event_id)
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=404, detail='Event not found')
    await session.execute(
        update(AlertEvent).where(AlertEvent.id == event_id).values(read=True)
    )
    await session.commit()
    return {'status': 'updated'}


@router.post('/events/read-all')
async def mark_all_read(
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await session.execute(
        update(AlertEvent).values(read=True)
    )
    await session.commit()
    return {'status': 'all-marked-read'}
