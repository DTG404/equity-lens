from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator


class TickerSymbol(BaseModel):
    value: str

    @field_validator('value')
    @classmethod
    def normalize_and_validate(cls, v: str) -> str:
        normalized = v.strip().upper()
        if not re.match(r'^[A-Z0-9.\-]{1,10}$', normalized):
            raise ValueError(
                f'Invalid ticker symbol: "{v}". Must be 1-10 alphanumeric, dot, or dash characters.'
            )
        return normalized


class WatchlistItem(BaseModel):
    symbol: str
    company_name: str = ''
    signal: str = Field(default='unrated')
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
