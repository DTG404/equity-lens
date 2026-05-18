"""Alert delivery via email and Discord."""

import logging
import smtplib
from email.mime.text import MIMEText
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_discord(message: str) -> bool:
    """Send a notification to Discord webhook."""
    webhook = settings.discord_webhook_url
    if not webhook:
        return False

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                webhook,
                json={'content': message[:2000]},
                timeout=10,
            )
            return resp.status_code == 204
    except Exception as e:
        logger.warning('Discord notification failed: %s', e)
        return False


def send_email(subject: str, body: str) -> bool:
    """Send an email notification via SMTP."""
    if not all([settings.smtp_host, settings.alert_email]):
        return False

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = settings.smtp_user or 'equity-lens@localhost'
        msg['To'] = settings.alert_email

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_user and settings.smtp_password:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.warning('Email notification failed: %s', e)
        return False


async def send_alert_notification(
    alert_type: str,
    symbol: str,
    message: str,
    severity: str,
) -> dict[str, Any]:
    """Send alert via all configured channels."""
    results: dict[str, bool] = {}

    formatted = f'[{severity.upper()}] {symbol}: {message}'

    # Discord
    discord_sent = await send_discord(formatted)
    results['discord'] = discord_sent

    # Email
    email_sent = send_email(f'Equity Lens Alert: {symbol} {alert_type}', formatted)
    results['email'] = email_sent

    return results
