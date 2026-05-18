from fastapi import APIRouter

from app.api.alert_routes import router as alert_router
from app.api.fundamentals_routes import router as fundamentals_router
from app.api.holdings_routes import router as holdings_router
from app.api.news_routes import router as news_router
from app.api.quote_routes import router as quote_router
from app.api.research_routes import router as research_router
from app.api.settings_routes import router as settings_router
from app.api.signals_routes import router as signals_router
from app.api.watchlist_routes import router as watchlist_router

router = APIRouter()
router.include_router(watchlist_router)
router.include_router(holdings_router)
router.include_router(research_router)
router.include_router(settings_router)
router.include_router(quote_router)
router.include_router(news_router)
router.include_router(alert_router)
router.include_router(fundamentals_router)
router.include_router(signals_router)


@router.get('/health')
def health() -> dict[str, str]:
    return {
        'service': 'equity-lens-api',
        'status': 'ok',
        'mode': 'local-first',
    }
