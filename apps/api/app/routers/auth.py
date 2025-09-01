import base64, os
from fastapi import APIRouter
from ..settings import settings

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
