import requests

from tasks import fetch_and_cache


def test_fetch_with_etag(tmp_path, monkeypatch):
    calls = []

    class Resp:
        def __init__(self, status_code, content=b"", etag=None):
            self.status_code = status_code
            self.content = content
            self.headers = {}
            if etag:
                self.headers["ETag"] = etag

        def raise_for_status(self):
            pass

    def fake_get(url, headers):
        calls.append(headers.get("If-None-Match"))
        if headers.get("If-None-Match") == "etag123":
            return Resp(304)
        return Resp(200, b"data", etag="etag123")

    monkeypatch.setattr(requests, "get", fake_get)

    dest = tmp_path / "file.csv"
    fetch_and_cache("http://example.com/file.csv", dest)
    assert dest.read_bytes() == b"data"

    fetch_and_cache("http://example.com/file.csv", dest)
    assert dest.read_bytes() == b"data"

    assert calls == [None, "etag123"]
