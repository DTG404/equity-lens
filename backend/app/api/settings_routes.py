"""Settings key-value endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import Setting

router = APIRouter(prefix='/settings', tags=['settings'])


class SettingsPutRequest(BaseModel):
    key: str
    value: str

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('key must not be empty')
        return v.strip()


@router.get('')
async def get_all_settings(
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(select(Setting))
    settings = result.scalars().all()
    return {s.key: s.value for s in settings}


@router.get('/{key}')
async def get_setting(
    key: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    if setting is None:
        raise HTTPException(status_code=404, detail=f'Setting "{key}" not found')
    return {'key': setting.key, 'value': setting.value}


@router.put('')
async def upsert_setting(
    body: SettingsPutRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(select(Setting).where(Setting.key == body.key))
    existing = result.scalar_one_or_none()
    if existing is not None:
        existing.value = body.value
    else:
        session.add(Setting(key=body.key, value=body.value))
    await session.flush()
    return {'key': body.key, 'value': body.value}
