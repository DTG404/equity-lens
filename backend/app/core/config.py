from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = 'sqlite:///./equity_lens.db'
    deepseek_api_key: str = ''
    market_data_provider: str = 'mock'
    news_data_provider: str = 'mock'
    quote_poll_seconds: int = 60
    news_poll_seconds: int = 300
    alert_eval_seconds: int = 30
    signal_eval_seconds: int = 3600
    fred_api_key: str = ''
    api_key: str = ''
    api_key_enabled: bool = False
    alpaca_api_key: str = ''
    alpaca_secret_key: str = ''
    alpaca_paper: bool = True
    finnhub_api_key: str = ''
    smtp_host: str = ''
    smtp_port: int = 587
    smtp_user: str = ''
    smtp_password: str = ''
    alert_email: str = ''
    discord_webhook_url: str = ''

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


settings = Settings()
