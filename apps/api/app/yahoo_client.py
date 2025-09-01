import random
import time
from typing import Optional, Dict

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models import OAuthToken, User
from .yahoo_oauth import YahooOAuthClient


class YahooFantasyClient:
    """Minimal Yahoo Fantasy Sports API client."""

    BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"

    def __init__(self, oauth_client: YahooOAuthClient):
        self.oauth_client = oauth_client

    def _request(
        self, db: Session, user: User, resource: str, params: Optional[Dict[str, str]] = None
    ) -> Dict:
        token = db.query(OAuthToken).filter_by(user_id=user.id, provider="yahoo").first()
        if not token:
            raise HTTPException(status_code=401, detail="Yahoo token not found")
        access = self.oauth_client.ensure_valid_token(db, token)
        url = f"{self.BASE_URL}{resource}"
        params = params or {}
        params.setdefault("format", "json")
        headers = {"Authorization": f"Bearer {access}"}
        for attempt in range(3):
            try:
                resp = httpx.get(url, params=params, headers=headers, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError:
                if attempt == 2:
                    raise
                time.sleep(0.1 * (2**attempt) + random.random() / 10)
        return {}

    def get(
        self, db: Session, user: User, resource: str, params: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Public GET wrapper"""
        return self._request(db, user, resource, params)
