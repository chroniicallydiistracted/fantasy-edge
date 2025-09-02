import os
import secrets
import base64
import hashlib
import json
from datetime import datetime, timedelta, UTC
from typing import Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from redis import Redis

from ..settings import settings
from ..deps import get_debug_user, get_db, get_token_encryption_service
from ..session import SessionManager
from ..models import User, OAuthToken
from ..security import TokenEncryptionService
from ..yahoo_oauth import YahooOAuthClient

router = APIRouter()

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
USERINFO_URL = "https://api.login.yahoo.com/openid/v1/userinfo"
SCOPE = "fspt-r"


def get_redis():
    """Get Redis client instance"""
    return Redis.from_url(settings.redis_url)


def generate_state_and_verifier():
    """Generate state and PKCE verifier for OAuth flow"""
    state = base64.urlsafe_b64encode(os.urandom(16)).decode()
    verifier = secrets.token_urlsafe(32)
    return state, verifier


def generate_code_challenge(verifier: str) -> str:
    """Generate PKCE code challenge from verifier"""
    challenge = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(challenge).decode().rstrip("=")


@router.get("/yahoo/login")
def yahoo_login(redis: Redis = Depends(get_redis)):
    """Initiate Yahoo OAuth flow with proper redirect"""
    state, verifier = generate_state_and_verifier()
    code_challenge = generate_code_challenge(verifier)

    # Store state and verifier in Redis
    redis.setex(
        f"yahoo:state:{state}", 
        600,  # 10 minutes TTL
        verifier
    )

    params = (
        f"client_id={settings.yahoo_client_id}&response_type=code&"
        f"redirect_uri={settings.yahoo_redirect_uri}&scope={SCOPE}&state={state}"
        f"&code_challenge={code_challenge}&code_challenge_method=S256"
    )

    # Return actual redirect response instead of JSON
    return RedirectResponse(f"{AUTH_URL}?{params}", status_code=302)


@router.get("/yahoo/callback")
def yahoo_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
    encryption: TokenEncryptionService = Depends(get_token_encryption_service),
    redis: Redis = Depends(get_redis),
):
    """Handle Yahoo OAuth callback, exchange code for tokens, and create session"""
    # Validate state
    verifier = redis.get(f"yahoo:state:{state}")
    if not verifier:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    # Clean up state
    redis.delete(f"yahoo:state:{state}")

    # Exchange code for tokens
    auth = f"{settings.yahoo_client_id}:{settings.yahoo_client_secret}"
    auth_header = base64.b64encode(auth.encode()).decode()

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.yahoo_redirect_uri,
        "code_verifier": verifier,
    }

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = httpx.post(TOKEN_URL, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        token_data = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {str(e)}")

    # Extract token information
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 0)
    guid = token_data.get("xoauth_yahoo_guid")
    scope = token_data.get("scope")

    # Get user info
    email = None
    try:
        userinfo_response = httpx.get(
            USERINFO_URL, 
            headers={"Authorization": f"Bearer {access_token}"}, 
            timeout=10
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        email = userinfo.get("email")
    except Exception:
        pass

    # Get or create user
    user = None
    if email:
        user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Encrypt tokens
    enc_access = encryption.encrypt(access_token)
    enc_refresh = encryption.encrypt(refresh_token) if refresh_token else None
    expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

    # Update or create OAuth token record
    oauth = db.query(OAuthToken).filter_by(user_id=user.id, provider="yahoo").first()
    if oauth:
        oauth.access_token = enc_access
        oauth.refresh_token = enc_refresh
        oauth.expires_at = expires_at
        oauth.scope = scope
        oauth.guid = guid
    else:
        oauth = OAuthToken(
            user_id=user.id,
            provider="yahoo",
            access_token=enc_access,
            refresh_token=enc_refresh,
            expires_at=expires_at,
            scope=scope,
            guid=guid,
        )
        db.add(oauth)
    db.commit()

    # Create session ID and store session data in Redis
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "provider": "yahoo",
        "user_id": user.id,
        "created_at": datetime.now(UTC).isoformat(),
        "expires_at": (datetime.now(UTC) + timedelta(seconds=settings.session_ttl_seconds)).isoformat(),
    }

    redis.setex(
        f"session:{session_id}",
        settings.session_ttl_seconds,
        json.dumps(session_data)
    )

    # Set session cookie
    response = RedirectResponse(f"{settings.web_base_url}/", status_code=302)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        path="/",
        secure=True,
        httponly=True,
        samesite="None",
        max_age=settings.session_ttl_seconds,
    )

    return response


@router.get("/me")
def get_me(
    response: Response,
    redis: Redis = Depends(get_redis),
):
    """Get current user session information"""
    session_id = response.cookies.get(settings.session_cookie_name)
    if not session_id:
        return {"ok": False, "error": "No session cookie"}

    session_data = redis.get(f"session:{session_id}")
    if not session_data:
        return {"ok": False, "error": "Session not found"}

    try:
        session_info = json.loads(session_data)
        return {"ok": True, "session": session_info}
    except Exception:
        return {"ok": False, "error": "Invalid session data"}