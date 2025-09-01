import json
from pathlib import Path

from app.yahoo_client import YahooFantasyClient


class DummyOAuth:
    def ensure_valid_token(self, db, token):
        return "token"


class DummyToken:
    pass


class DummyQuery:
    def filter_by(self, **kwargs):
        return self

    def first(self):
        return DummyToken()


class DummyDB:
    def query(self, model):
        return DummyQuery()


class DummyUser:
    id = 1


def test_snapshot_creates_file(monkeypatch, tmp_path):
    client = YahooFantasyClient(DummyOAuth())
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        client,
        "_request",
        lambda db, user, resource, params: {"data": 1},
    )
    client.snapshot(DummyDB(), DummyUser(), "/team/1/roster")
    path = tmp_path / "snapshots" / "team_1_roster.json"
    assert path.exists()
    with path.open() as f:
        assert json.load(f) == {"data": 1}
