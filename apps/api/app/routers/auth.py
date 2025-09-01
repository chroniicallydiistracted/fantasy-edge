import base64, os
from fastapi import APIRouter, Depends, Response
from ..settings import settings
from ..deps import get_debug_user
from ..session import SessionManager
from ..models import User

router = APIRouter()

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
SCOPE = "fspt-r"

@router.get("/yahoo/login")
def yahoo_login():
    state = base64.urlsafe_b64encode(os.urandom(16)).decode()
    params = (
        f"client_id={settings.yahoo_client_id}&response_type=code&"
        f"redirect_uri={settings.yahoo_redirect_uri}&scope={SCOPE}&state={state}"
    )
    return {"redirect": f"{AUTH_URL}?{params}"}

@router.get("/yahoo/callback")
def yahoo_callback(code: str, state: str):
    # Stub: exchange handled in later step
    return {"received_code": code, "state": state}

@router.get("/session/debug", response_model=dict)
def debug_session(
    response: Response,
    current_user: User = Depends(get_debug_user)
):
    """Debug session endpoint - sets session cookie for dev user if enabled"""
    if not settings.allow_debug_user:
        return {"error": "Debug user not enabled"}
    
    if current_user:
        # Set session cookie for the debug user
        SessionManager.set_session_cookie(response, current_user.id)
        return {"ok": True, "user_id": current_user.id}
    
    return {"error": "Invalid debug user header"}
