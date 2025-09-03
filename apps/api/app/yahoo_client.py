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
        self.max_retries = 3

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
        for attempt in range(self.max_retries):
            try:
                resp = httpx.get(url, params=params, headers=headers, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError:
                if attempt == self.max_retries - 1:
                    raise
                base = 0.1 * (2**attempt)
                jitter = random.uniform(0, 0.1)
                time.sleep(base + jitter)
        return {}

    def get(
        self, db: Session, user: User, resource: str, params: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Public GET wrapper"""
        return self._request(db, user, resource, params)

    def snapshot(
        self, db: Session, user: User, resource: str, params: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Fetch a resource and persist the JSON snapshot to disk."""
        data = self._request(db, user, resource, params)
        path = f"snapshots/{resource.strip('/').replace('/', '_')}.json"
        import os

        os.makedirs("snapshots", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            import json

            json.dump(data, f)
        return data
