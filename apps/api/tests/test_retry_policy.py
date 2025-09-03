import random
import time
import httpx

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


def test_exponential_backoff(monkeypatch):
    client = YahooFantasyClient(DummyOAuth())

    calls = {"count": 0}

    def fake_get(url, params, headers, timeout):
        if calls["count"] < 2:
            calls["count"] += 1
            raise httpx.HTTPError("boom")

        class Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return {"ok": True}

        return Resp()

    sleeps = []
    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(time, "sleep", lambda x: sleeps.append(x))
    monkeypatch.setattr(random, "uniform", lambda a, b: 0)

    data = client.get(DummyDB(), DummyUser(), "/test")
    assert data == {"ok": True}
    assert sleeps == [0.1, 0.2]
