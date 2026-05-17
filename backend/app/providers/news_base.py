"""News provider protocol and data model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from app.domain.models import TickerSymbol


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    summary: str
    published_at: datetime


class NewsProvider(Protocol):
    def fetch_news(self, symbol: TickerSymbol, max_results: int = 10) -> list[dict[str, Any]]: ...
