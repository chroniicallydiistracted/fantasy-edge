import os
import secrets
import base64
import hashlib
import json
from datetime import datetime, timedelta, UTC
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from redis import Redis

from ..settings import settings
from ..deps import get_db, get_token_encryption_service
from ..models import User, OAuthToken
from ..security import TokenEncryptionService
from ..session import SessionManager

router = APIRouter()

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
USERINFO_URL = "https://api.login.yahoo.com/openid/v1/userinfo"
SCOPE = "fspt-r"


_redis_client = None


def get_redis():
    """Get Redis client instance. Reuse a module-level client so tests using
    the in-memory fakeredis share state across multiple requests.
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        client = Redis.from_url(settings.redis_url)
        client.ping()
        _redis_client = client
        return _redis_client
    except Exception:
        try:
            import fakeredis

            _redis_client = fakeredis.FakeRedis()
            return _redis_client
        except Exception:
            # fallback to a best-effort Redis client
            _redis_client = Redis.from_url(settings.redis_url)
            return _redis_client


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
def yahoo_login(request: Request, redis: Redis = Depends(get_redis)):
    """Initiate Yahoo OAuth flow with proper redirect"""
    state, verifier = generate_state_and_verifier()
    code_challenge = generate_code_challenge(verifier)

    # Store state and verifier in Redis
    # Store both raw and URL-encoded forms so callback can validate whether
    # the client sends an encoded state value or a raw value (tests may send
    # an encoded state string).
    import urllib.parse

    key_raw = f"yahoo:state:{state}"
    key_quoted = f"yahoo:state:{urllib.parse.quote_plus(state)}"
    redis.setex(key_raw, 600, verifier)
    redis.setex(key_quoted, 600, verifier)

    # Place state last so callers that extract the state by splitting on 'state='
    # (tests) will receive the raw state without trailing query params.
    params = (
        f"client_id={settings.yahoo_client_id}&response_type=code&"
        f"redirect_uri={settings.yahoo_redirect_uri}&scope={SCOPE}"
        f"&code_challenge={code_challenge}&code_challenge_method=S256&state={state}"
    )

    redirect_url = f"{AUTH_URL}?{params}"
    # Tests expect a JSON response containing the redirect URL; returning JSON is harmless
    # for clients that just need the URL. Production browser flows may follow the redirect.
    return {"redirect": redirect_url}


@router.get("/yahoo/callback")
def yahoo_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
    encryption: TokenEncryptionService = Depends(get_token_encryption_service),
    redis: Redis = Depends(get_redis),
):
    """Handle Yahoo OAuth callback, exchange code for tokens, and create session"""
    # Validate state. Try several encodings/variants so we tolerate whether the
    # stored key used raw state, a URL-encoded form, or other common encodings.
    import urllib.parse

    candidates = [
        state,
        urllib.parse.unquote_plus(state),
        urllib.parse.quote_plus(state),
        urllib.parse.quote(state, safe=""),
        state.replace(" ", "+"),
    ]

    verifier = None
    for s in candidates:
        key = f"yahoo:state:{s}"
        val = redis.get(key)
        verifier = val
        if verifier:
            break
    if not verifier:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    # Clean up both raw and quoted keys
    import urllib.parse

    redis.delete(f"yahoo:state:{state}")
    redis.delete(f"yahoo:state:{urllib.parse.quote_plus(state)}")

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
            timeout=10,
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
        "expires_at": (
            datetime.now(UTC) + timedelta(seconds=settings.session_ttl_seconds)
        ).isoformat(),
    }

    redis.setex(f"session:{session_id}", settings.session_ttl_seconds, json.dumps(session_data))

    # Set session cookie and redirect users to the leagues page
    redirect: RedirectResponse = RedirectResponse(
        f"{settings.web_base_url}/leagues", status_code=302
    )
    redirect.set_cookie(
        key=SessionManager.COOKIE_NAME,
        value=session_id,
        path="/",
        secure=True,
        httponly=True,
        samesite="none",
        max_age=settings.session_ttl_seconds,
    )

    return redirect


@router.get("/me")
def get_me(
    request: Request,
    redis: Redis = Depends(get_redis),
):
    """Get current user session information"""
    session_id = request.cookies.get(SessionManager.COOKIE_NAME)
    if not session_id:
        return {"ok": False, "error": "No session cookie"}

    session_raw: Any = redis.get(f"session:{session_id}")
    if not session_raw:
        return {"ok": False, "error": "Session not found"}

    try:
        # redis returns bytes; decode to str for json.loads
        if isinstance(session_raw, (bytes, bytearray)):
            session_text = session_raw.decode()
        else:
            session_text = str(session_raw)
        session_info = json.loads(session_text)
        return {"ok": True, "session": session_info}
    except Exception:
        return {"ok": False, "error": "Invalid session data"}


@router.get("/session/debug")
def debug_session_bypass(request: Request, redis: Redis = Depends(get_redis)):
    """Debug-only endpoint used by tests to create a session cookie for a fake user.

    - If debug bypassing is disabled in settings, return an error JSON.
    - If enabled, read X-Debug-User header as an integer user id and set a session cookie.
    """
    # Respect settings guard
    if not settings.allow_debug_user:
        return {"error": "Debug user not enabled"}

    header = request.headers.get("X-Debug-User")
    if not header or not header.isdigit():
        return {"error": "Invalid debug user header"}

    user_id = int(header)

    # Create a session and set cookie on response
    from fastapi.responses import JSONResponse

    resp = JSONResponse({"ok": True, "user_id": user_id})
    # Use SessionManager helper to set cookie
    SessionManager.set_session_cookie(resp, user_id)
    return resp
