from datetime import datetime, timedelta

import respx

from app.models import User, OAuthToken
from app.security import TokenEncryptionService
from app.settings import settings


def _setup_user(db_session):
    user = User(email=None)
    db_session.add(user)
    db_session.commit()
    enc = TokenEncryptionService(settings.token_crypto_key)
    token = OAuthToken(
        user_id=user.id,
        provider="yahoo",
        access_token=enc.encrypt("old"),
        refresh_token=enc.encrypt("refresh"),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    db_session.add(token)
    db_session.commit()
    return user, token, enc


def _auth_client(client, user):
    original = settings.allow_debug_user
    settings.allow_debug_user = True
    client.get("/auth/session/debug", headers={"X-Debug-User": str(user.id)})
    settings.allow_debug_user = original


def test_requires_auth(client):
    resp = client.get("/yahoo/leagues")
    assert resp.status_code == 401


def test_list_leagues(client, db_session):
    user, token, enc = _setup_user(db_session)
    _auth_client(client, user)
    with respx.mock() as mock:
        mock.get(
            "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=nfl/leagues",
            params={"format": "json"},
        ).respond(200, json={"fantasy_content": {"leagues": []}})
        resp = client.get("/yahoo/leagues")
    assert resp.status_code == 200
    assert resp.json()["fantasy_content"]["leagues"] == []


def test_league_meta_scoring(client, db_session):
    user, token, enc = _setup_user(db_session)
    _auth_client(client, user)
    league_json = {
        "fantasy_content": {
            "league": {
                "settings": {
                    "stat_categories": {"stats": [{"stat": {"stat_id": 1, "name": "Points"}}]}
                }
            }
        }
    }
    with respx.mock() as mock:
        mock.get(
            "https://fantasysports.yahooapis.com/fantasy/v2/league/123",
            params={"format": "json"},
        ).respond(200, json=league_json)
        resp = client.get("/yahoo/league/123")
    assert resp.status_code == 200
    body = resp.json()
    assert body["raw"] == league_json
    assert body["scoring"] == {"1": "Points"}


def test_league_teams_rosters_matchups(client, db_session):
    user, token, enc = _setup_user(db_session)
    _auth_client(client, user)
    with respx.mock() as mock:
        mock.get(
            "https://fantasysports.yahooapis.com/fantasy/v2/league/123/teams",
            params={"format": "json"},
        ).respond(200, json={"teams": []})
        mock.get(
            "https://fantasysports.yahooapis.com/fantasy/v2/league/123/rosters",
            params={"format": "json", "week": "5"},
        ).respond(200, json={"rosters": []})
        mock.get(
            "https://fantasysports.yahooapis.com/fantasy/v2/league/123/matchups",
            params={"format": "json", "week": "5"},
        ).respond(200, json={"matchups": []})
        teams = client.get("/yahoo/league/123/teams")
        rosters = client.get("/yahoo/league/123/rosters", params={"week": 5})
        matchups = client.get("/yahoo/league/123/matchups", params={"week": 5})
    assert teams.status_code == 200 and teams.json() == {"teams": []}
    assert rosters.status_code == 200 and rosters.json() == {"rosters": []}
    assert matchups.status_code == 200 and matchups.json() == {"matchups": []}


def test_refresh_path(client, db_session):
    user, token, enc = _setup_user(db_session)
    token.expires_at = datetime.utcnow() + timedelta(minutes=4)
    db_session.add(token)
    db_session.commit()
    _auth_client(client, user)
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
        mock.get(
            "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=nfl/leagues",
            params={"format": "json"},
        ).respond(200, json={"fantasy_content": {}})
        resp = client.get("/yahoo/leagues")
    assert resp.status_code == 200
    db_session.refresh(token)
    assert enc.decrypt(token.access_token) == "new"
