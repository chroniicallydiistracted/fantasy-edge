from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ff:ff@db:5432/ff"
    redis_url: str = "redis://redis:6379/0"
    yahoo_client_id: str = ""
    yahoo_client_secret: str = ""
    yahoo_redirect_uri: str = "http://localhost:8000/auth/yahoo/callback"
    jwt_secret: str = "change-me"
    token_crypto_key: str = "REPLACE_ME"  # 32+ character key for Fernet encryption
    allow_debug_user: bool = False  # Enable debug bypass header
    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://misfits.westfam.media",
    ]
    nws_user_agent: str = "League of Misfits Edge (contact: you@example.com)"

    class Config:
        env_file = ".env"

settings = Settings()
