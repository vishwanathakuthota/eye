from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Project Eye API"
    app_version: str = "v0.1.0-alpha"
    app_env: str = Field(default="development", alias="EYE_APP_ENV")
    service_name: str = "eye-api"
    api_v1_prefix: str = "/api/v1"
    api_host: str = Field(default="0.0.0.0", alias="EYE_API_HOST")
    api_port: int = Field(default=8000, alias="EYE_API_PORT")
    api_cors_origins_raw: str = Field(
        default="http://localhost:3000",
        alias="EYE_API_CORS_ORIGINS",
    )
    database_url: str = Field(
        default="postgresql+psycopg://eye:eye_password@localhost:5432/eye",
        alias="EYE_DATABASE_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def api_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
