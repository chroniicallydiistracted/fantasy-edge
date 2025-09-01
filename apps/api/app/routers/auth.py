import base64
import os
from datetime import datetime, timedelta, UTC
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..settings import settings
from ..deps import get_debug_user, get_db, get_token_encryption_service
from ..session import SessionManager
from ..models import User, OAuthToken
from ..security import TokenEncryptionService
from ..yahoo_oauth import YahooOAuthClient

router = APIRouter()

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
SCOPE = "fspt-r openid profile email"
state_store: Dict[str, datetime] = {}


@router.get("/yahoo/login")
def yahoo_login():
    state = base64.urlsafe_b64encode(os.urandom(16)).decode()
    state_store[state] = datetime.now(UTC)
    params = (
        f"client_id={settings.yahoo_client_id}&response_type=code&"
        f"redirect_uri={settings.yahoo_redirect_uri}&scope={SCOPE}&state={state}"
    )
    return {"redirect": f"{AUTH_URL}?{params}"}


@router.get("/yahoo/callback")
def yahoo_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
    encryption: TokenEncryptionService = Depends(get_token_encryption_service),
):
    if state not in state_store:
        raise HTTPException(status_code=400, detail="Invalid state")
    state_store.pop(state, None)

    client = YahooOAuthClient(encryption)
    token_data = client.exchange_code(code)
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 0)
    guid = token_data.get("xoauth_yahoo_guid")
    scope = token_data.get("scope")
    email = None
    try:
        userinfo = client.fetch_userinfo(access_token)
        email = userinfo.get("email")
    except Exception:
        pass

    user = None
    if email:
        user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    enc_access = encryption.encrypt(access_token)
    enc_refresh = encryption.encrypt(refresh_token) if refresh_token else None
    expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

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

    redirect = RedirectResponse(url="/leagues")
    SessionManager.set_session_cookie(redirect, user.id)
    return redirect


@router.get("/session/debug", response_model=dict)
def debug_session(
    response: Response,
    current_user: User = Depends(get_debug_user),
):
    """Debug session endpoint - sets session cookie for dev user if enabled"""
    if not settings.allow_debug_user:
        return {"error": "Debug user not enabled"}

    if current_user:
        # Set session cookie for the debug user
        SessionManager.set_session_cookie(response, current_user.id)
        return {"ok": True, "user_id": current_user.id}

    return {"error": "Invalid debug user header"}
