import requests

from tasks import compute_waf, update_weather


def test_compute_waf():
    forecast = {
        "properties": {
            "periods": [
                {
                    "windSpeed": "20 mph",
                    "probabilityOfPrecipitation": {"value": 60},
                }
            ]
        }
    }
    assert compute_waf(forecast) == 0.8


def test_update_weather_uses_user_agent(monkeypatch):
    called = {}

    class Resp:
        def __init__(self):
            self.status_code = 200
            self.headers = {}

        def json(self):
            return {
                "properties": {
                    "periods": [
                        {
                            "windSpeed": "0 mph",
                            "probabilityOfPrecipitation": {"value": 0},
                        }
                    ]
                }
            }

        def raise_for_status(self):
            pass

    def fake_get(url, headers):
        called["headers"] = headers
        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    waf = update_weather("game1", 0.0, 0.0)
    assert called["headers"]["User-Agent"].startswith("Fantasy Edge")
    assert waf == 1.0
