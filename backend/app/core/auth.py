"""Simple API key authentication dependency."""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


async def verify_api_key(api_key: str | None = Depends(api_key_header)) -> None:
    """Verify the API key if auth is enabled. Skip check if disabled."""
    if not settings.api_key_enabled:
        return
    if not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or missing API key',
        )
