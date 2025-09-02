# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from cryptography.fernet import Fernet


class Settings(BaseSettings):
    # Load from env (and .env if present). Ignore unknown envs to avoid "extra" errors.
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )

    # --- Required secrets / URLs (fail fast if missing) ---
    token_crypto_key: str = Field(
        ..., alias="TOKEN_CRYPTO_KEY"
    )  # Fernet 32-byte urlsafe base64
    database_url: str = Field(
        ..., alias="DATABASE_URL"
    )  # e.g. postgresql+psycopg://...
    redis_url: str = Field(..., alias="REDIS_URL")  # e.g. rediss://:<pwd>@host:6380/0
    yahoo_client_id: str = Field(..., alias="YAHOO_CLIENT_ID")
    yahoo_client_secret: str = Field(..., alias="YAHOO_CLIENT_SECRET")
    yahoo_redirect_uri: str = Field(..., alias="YAHOO_REDIRECT_URI")
    web_base_url: str = Field(
        ..., alias="WEB_BASE_URL"
    )  # e.g. https://misfits.westfam.media
    jwt_secret: str = Field(..., alias="JWT_SECRET")

    # --- App behavior (sane defaults, override via env) ---
    allow_debug_user: bool = Field(False, alias="ALLOW_DEBUG_USER")
    cors_origins: str = Field("", alias="CORS_ORIGINS")  # comma-separated list
    nws_user_agent: str = Field(
        "Fantasy Edge (contact: chroniicallydiistracted@gmail.com)",
        alias="NWS_USER_AGENT",
    )
    live_poll_interval: int = Field(8000, alias="LIVE_POLL_INTERVAL")  # ms
    live_provider: str = Field(
        "yahoo", alias="LIVE_PROVIDER"
    )  # "yahoo" | "espn" | etc.
    session_cookie_name: str = Field("fe_session", alias="SESSION_COOKIE_NAME")
    session_ttl_seconds: int = Field(2592000, alias="SESSION_TTL_SECONDS")  # 30 days

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Returns parsed CORS origins. If ALLOW_DEBUG_USER is true and nothing is set,
        allow http://localhost:3000 for local dev only.
        """
        origins: list[str] = []
        if self.cors_origins:
            origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        if self.allow_debug_user and "http://localhost:3000" not in origins:
            origins.append("http://localhost:3000")
        return origins

    # Validate Fernet key early with a friendly error if malformed
    @field_validator("token_crypto_key")
    @classmethod
    def _validate_fernet_key(cls, v: str) -> str:
        Fernet(v)  # will raise ValueError if not 32-byte urlsafe base64
        return v


# IMPORTANT: instantiate outside the class
settings = Settings()
