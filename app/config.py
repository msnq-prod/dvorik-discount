from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: str
    TZ: str
    DB_URL: str
    REDIS_URL: str
    TELEGRAM_MAIN_BOT_TOKEN: str
    TELEGRAM_AUTH_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_MAIN_URL: str
    TELEGRAM_WEBHOOK_AUTH_URL: str
    TELEGRAM_CHANNEL_ID: str
    FIRST_SUPERADMIN_TG_ID: int
    DEFAULT_BROADCAST_RATE_PER_MINUTE: int
    DEFAULT_BROADCAST_BATCH_SIZE: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MONTHLY_DISCOUNT_INTERVAL_DAYS: int = 30
    DISCOUNT_CODE_PREFIX: str = "КОД"


settings = Settings()
