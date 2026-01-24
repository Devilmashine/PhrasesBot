from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Глобальные настройки приложения.
    Используем pydantic-settings v2 с загрузкой переменных из .env.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    openai_tokens: str  # список ключей через запятую
    sqlalchemy_url: str = "sqlite+aiosqlite:///db.sqlite3"
    admin_ids: str = ""  # список TG ID админов через запятую

    @property
    def openai_keys(self) -> list[str]:
        return [key.strip() for key in self.openai_tokens.split(",") if key.strip()]

    @property
    def admin_id_list(self) -> list[int]:
        return [int(raw) for raw in self.admin_ids.split(",") if raw.strip()]


settings = Settings()
