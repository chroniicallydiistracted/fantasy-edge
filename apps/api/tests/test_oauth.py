from datetime import datetime, timedelta

import respx

from app.models import OAuthToken, User
from app.security import TokenEncryptionService
from app.settings import settings
from app.yahoo_oauth import YahooOAuthClient
from app.session import SessionManager


def test_yahoo_login_and_callback_flow(client, db_session):
    with respx.mock() as mock:
        token_json = {
            "access_token": "atoken",
            "refresh_token": "rtoken",
            "expires_in": 3600,
            "scope": "fspt-r",
            "xoauth_yahoo_guid": "ABC123",
        }
        mock.post("https://api.login.yahoo.com/oauth2/get_token").respond(200, json=token_json)
        mock.get("https://api.login.yahoo.com/openid/v1/userinfo").respond(
            200, json={"email": "user@example.com"}
        )

        login_resp = client.get("/auth/yahoo/login")
        state = login_resp.json()["redirect"].split("state=")[-1]

        resp = client.get(
            "/auth/yahoo/callback",
            params={"code": "123", "state": state},
            follow_redirects=False,
        )

    assert resp.status_code in (302, 307)
    assert SessionManager.COOKIE_NAME in resp.headers.get("set-cookie", "")
    assert resp.headers["location"].endswith("/leagues")

    token = db_session.query(OAuthToken).first()
    assert token is not None
    enc = TokenEncryptionService(settings.token_crypto_key)
    assert enc.decrypt(token.access_token) == "atoken"


def test_state_mismatch_returns_error(client):
    resp = client.get("/auth/yahoo/callback", params={"code": "abc", "state": "bad"})
    assert resp.status_code == 400


def test_refresh_token_if_expiring(db_session):
    enc = TokenEncryptionService(settings.token_crypto_key)
    user = User(email=None)
    db_session.add(user)
    db_session.commit()
    token = OAuthToken(
        user_id=user.id,
        provider="yahoo",
        access_token=enc.encrypt("old"),
        refresh_token=enc.encrypt("refresh"),
        expires_at=datetime.utcnow() + timedelta(minutes=4),
    )
    db_session.add(token)
    db_session.commit()

    with respx.mock() as mock:
        mock.post("https://api.login.yahoo.com/oauth2/get_token").respond(
            200,
            json={
                "access_token": "new",
                "refresh_token": "newrefresh",
                "expires_in": 3600,
                "scope": "fspt-r",
                "xoauth_yahoo_guid": "ABC123",
            },
        )
        client_obj = YahooOAuthClient(enc)
        access = client_obj.ensure_valid_token(db_session, token)

    assert access == "new"
    assert enc.decrypt(token.access_token) == "new"
