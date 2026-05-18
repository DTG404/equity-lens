"""Alert notification settings endpoint."""

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get('/status')
async def notification_status() -> dict[str, Any]:
    """Check which notification channels are configured."""
    from app.core.config import settings
    return {
        'discord': bool(settings.discord_webhook_url),
        'email': bool(settings.smtp_host and settings.alert_email),
    }


@router.post('/test')
async def test_notification() -> dict[str, Any]:
    """Send a test notification to all configured channels."""
    from app.core.notifications import send_alert_notification
    results = await send_alert_notification(
        alert_type='test',
        symbol='SYSTEM',
        message='This is a test notification from Equity Lens.',
        severity='info',
    )
    return results
