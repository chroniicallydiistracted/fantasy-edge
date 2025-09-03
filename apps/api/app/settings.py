from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from cryptography.fernet import Fernet

# Load .env from apps/api/.env (adjust if yours is elsewhere)
ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        case_sensitive=False,
    )

    # --- required in production; safe defaults for tests ---
    database_url: str = Field("sqlite://", alias="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    yahoo_client_id: str = Field("test-client", alias="YAHOO_CLIENT_ID")
    yahoo_client_secret: str = Field("test-secret", alias="YAHOO_CLIENT_SECRET")
    jwt_secret: str = Field("test-jwt-secret", alias="JWT_SECRET")
    token_crypto_key: str = Field(
        "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
        alias="TOKEN_CRYPTO_KEY",
    )

    # --- non-secrets with defaults (quiet editor) ---
    yahoo_redirect_uri: str = Field(
        "https://api.misfits.westfam.media/auth/yahoo/callback",
        alias="YAHOO_REDIRECT_URI",
    )
    web_base_url: str = Field("https://misfits.westfam.media", alias="WEB_BASE_URL")
    allow_debug_user: bool = Field(False, alias="ALLOW_DEBUG_USER")
    cors_origins: str = Field(
        "http://localhost:3000,https://misfits.westfam.media", alias="CORS_ORIGINS"
    )
    nws_user_agent: str = Field(
        "Fantasy Edge (contact: chroniicallydiistracted@gmail.com)",
        alias="NWS_USER_AGENT",
    )
    live_poll_interval: int = Field(8000, alias="LIVE_POLL_INTERVAL")
    live_provider: str = Field("yahoo", alias="LIVE_PROVIDER")
    session_cookie_name: str = Field("fe_session", alias="SESSION_COOKIE_NAME")
    session_ttl_seconds: int = Field(2592000, alias="SESSION_TTL_SECONDS")  # 30d

    @property
    def cors_origins_list(self) -> list[str]:
        items = [o.strip() for o in (self.cors_origins or "").split(",") if o.strip()]
        return items

    @field_validator("token_crypto_key")
    @classmethod
    def _validate_fernet_key(cls, v: str) -> str:
        Fernet(v)  # raises if not a 32-byte urlsafe b64 string (44 chars)
        return v


# Instantiate; static checkers can’t see env injection, so ignore the warning here.
settings = Settings()  # pyright: ignore[reportCallIssue]
