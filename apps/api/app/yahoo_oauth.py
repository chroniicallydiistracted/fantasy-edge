import base64
import random
import time
from datetime import datetime, timedelta, UTC
from typing import Dict

import httpx
from sqlalchemy.orm import Session

from .models import OAuthToken
from .security import TokenEncryptionService
from .settings import settings

TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
USERINFO_URL = "https://api.login.yahoo.com/openid/v1/userinfo"


class YahooOAuthClient:
    """Client for handling Yahoo OAuth token exchange and refresh."""

    def __init__(self, encryption: TokenEncryptionService):
        auth = f"{settings.yahoo_client_id}:{settings.yahoo_client_secret}"
        self.auth_header = base64.b64encode(auth.encode()).decode()
        self.encryption = encryption

    def _post(self, data: Dict[str, str]) -> Dict[str, str]:
        headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        # basic retry with jitter
        for attempt in range(3):
            try:
                response = httpx.post(TOKEN_URL, data=data, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                if attempt == 2:
                    raise
                time.sleep(0.1 * (2**attempt) + random.random() / 10)
        return {}

    def exchange_code(self, code: str) -> Dict[str, str]:
        data = {
            "code": code,
            "redirect_uri": settings.yahoo_redirect_uri,
            "grant_type": "authorization_code",
        }
        return self._post(data)

    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        data = {
            "refresh_token": refresh_token,
            "redirect_uri": settings.yahoo_redirect_uri,
            "grant_type": "refresh_token",
        }
        return self._post(data)

    def fetch_userinfo(self, access_token: str) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get(USERINFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def ensure_valid_token(self, db: Session, token: OAuthToken) -> str:
        """Return decrypted access token, refreshing if expiring soon."""
        if token.expires_at:
            expires = token.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=UTC)
            if expires - datetime.now(UTC) < timedelta(minutes=5):
                data = self.refresh_token(self.encryption.decrypt(token.refresh_token))
                token.access_token = self.encryption.encrypt(data["access_token"])
                if data.get("refresh_token"):
                    token.refresh_token = self.encryption.encrypt(data["refresh_token"])
                token.expires_at = datetime.now(UTC) + timedelta(
                    seconds=int(data.get("expires_in", 0))
                )
                token.scope = data.get("scope")
                db.add(token)
                db.commit()
                db.refresh(token)
        return self.encryption.decrypt(token.access_token)
