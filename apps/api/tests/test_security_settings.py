from fastapi import Response

from app.session import SessionManager
from app.settings import settings


def test_cookie_prod(monkeypatch):
    resp = Response()
    monkeypatch.setattr(settings, "allow_debug_user", False)
    SessionManager.set_session_cookie(resp, 1)
    cookie = resp.headers.get("set-cookie")
    assert "Secure" in cookie
    assert "SameSite=None" in cookie


def test_cookie_dev(monkeypatch):
    resp = Response()
    monkeypatch.setattr(settings, "allow_debug_user", True)
    SessionManager.set_session_cookie(resp, 1)
    cookie = resp.headers.get("set-cookie")
    assert "Secure" not in cookie
    assert "SameSite=Lax" in cookie


def test_cors_defaults():
    assert "http://localhost:3000" in settings.cors_origins
    assert "https://misfits.westfam.media" in settings.cors_origins
