from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ============================================================
    # Application
    # ============================================================

    APP_NAME: str = "Psicomichi API"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    # ============================================================
    # Database - PostgreSQL
    # ============================================================

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "psicomichi_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:"
        "postgres@localhost:5432/psicomichi_db"
    )

    # ============================================================
    # Security - JWT
    # ============================================================

    SECRET_KEY: str = Field(min_length=32)

    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, gt=0)

    # ============================================================
    # Rate limiting - Authentication
    # ============================================================

    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = Field(default=5, gt=0)
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, gt=0)

    # ============================================================
    # Frontend / CORS
    # ============================================================

    FRONTEND_URL: str = "http://localhost:5173"

    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    # ============================================================
    # Refresh token cookie
    # ============================================================

    REFRESH_COOKIE_NAME: str = "psicomichi_refresh_token"
    REFRESH_COOKIE_PATH: str = "/api/v1/auth"
    REFRESH_COOKIE_HTTPONLY: bool = True
    REFRESH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_MAX_AGE_SECONDS: int = Field(
        default=60 * 60 * 24 * 30,
        gt=0,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()