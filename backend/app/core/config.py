from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = 'sqlite:///./equity_lens.db'
    deepseek_api_key: str = ''
    market_data_provider: str = 'mock'
    news_data_provider: str = 'mock'
    quote_poll_seconds: int = 60

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )


settings = Settings()
