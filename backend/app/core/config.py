"""Typed application settings loaded from the environment / .env file."""

import secrets
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Runtime configuration for the API.

    Every value can be overridden with an environment variable of the same
    (upper-cased) name, e.g. ``GEMINI_API_KEY``.
    """

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application -------------------------------------------------
    app_name: str = "Asesor IA API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    # --- CORS --------------------------------------------------------
    # "*" keeps the Flutter emulator/device demo frictionless. Restrict it
    # for any non-local deployment.
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # --- Gemini ------------------------------------------------------
    gemini_api_key: str | None = None
    enable_experimental_ai: bool = False
    # `gemini-1.5-flash` was shut down by Google; `gemini-flash-latest` is the
    # hot-swapped alias of the current stable Flash model. Override with
    # GEMINI_MODEL when you need to pin an exact version.
    gemini_model: str = "gemini-flash-latest"
    gemini_timeout_seconds: int = 60
    gemini_max_output_tokens: int = 2048

    # --- Persistence -------------------------------------------------
    # SQLite keeps the demo runnable with zero infrastructure. Point
    # DATABASE_URL at PostgreSQL (pgvector) for the production-shaped setup.
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'asesor_ia.db'}"
    sql_echo: bool = False

    # --- Media storage -----------------------------------------------
    storage_dir: Path = BASE_DIR / "data" / "storage"
    media_url_prefix: str = "/api/v1/media"
    max_upload_mb: int = 8
    image_max_side: int = 1024

    # --- INCI cache ---------------------------------------------------
    redis_url: str | None = None
    inci_cache_ttl_seconds: int = 60 * 60 * 24

    # --- Monetization ------------------------------------------------
    # Affiliate links are generated from this template instead of trusting a
    # model to invent URLs. Replace with your tracking tag in production.
    affiliate_search_template: str = "https://www.amazon.com/s?k={query}"
    affiliate_tag: str = ""

    # --- Demo identity (no auth in Phase 1) ---------------------------
    demo_user_email: str = "demo@asesor.ia"
    demo_user_name: str = "Demo User"

    # --- Auth / JWT ----------------------------------------------------
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def gemini_enabled(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.strip())

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
