"""Macroeconomic data API endpoint."""

from typing import Any

from fastapi import APIRouter

from app.providers.fred import get_macro_data

router = APIRouter(prefix='/macro', tags=['macro'])


@router.get('')
async def get_macro() -> dict[str, Any]:
    """Fetch latest macroeconomic indicators from FRED."""
    return get_macro_data()
