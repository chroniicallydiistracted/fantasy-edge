from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ff:ff@db:5432/ff"
    redis_url: str = "redis://redis:6379/0"
    yahoo_client_id: str = ""
    yahoo_client_secret: str = ""
    yahoo_redirect_uri: str = "http://localhost:8000/auth/yahoo/callback"
    jwt_secret: str = "REPLACE_ME"
    token_crypto_key: str = "REPLACE_ME"  # base64-encoded 32-byte key for Fernet encryption
    allow_debug_user: bool = False  # Enable debug bypass header
    cors_origins: str = ""  # Comma-separated origins from env var
    nws_user_agent: str = "Fantasy Edge (contact: you@example.com)"
    live_poll_interval: int = 8000  # milliseconds between polling for game data

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins with localhost for development if not in production"""
        origins = []

        # Parse comma-separated origins from env var
        if self.cors_origins:
            origins = [origin.strip() for origin in str(self.cors_origins).split(",") if origin.strip()]

        # Add localhost for development if not already present and debug mode is enabled
        if self.allow_debug_user and "localhost:3000" not in origins:
            origins.append("http://localhost:3000")

        # Ensure we have at least one origin for security
        if not origins:
            origins = ["http://localhost:3000"] if self.allow_debug_user else []

        return origins

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
