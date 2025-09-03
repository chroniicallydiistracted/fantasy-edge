import importlib
from datetime import timedelta


def test_schedule_env(monkeypatch):
    monkeypatch.setenv("NIGHTLY_SYNC_CRON", "5 4 * * *")
    monkeypatch.setenv("WAIVER_SHORTLIST_CRON", "0 8 * * WED")
    monkeypatch.setenv("GAMEDAY_REFRESH_MINUTES", "5")
    import celery_app

    importlib.reload(celery_app)
    beat = celery_app.celery.conf.beat_schedule

    nightly = beat["nightly-sync"]["schedule"]
    assert nightly._orig_minute == "5"
    assert nightly._orig_hour == "4"

    waiver = beat["tuesday-waivers"]["schedule"]
    assert waiver._orig_hour == "8"
    assert waiver._orig_day_of_week.lower() == "wed"

    refresh = beat["gameday-refresh"]["schedule"]
    assert isinstance(refresh, timedelta)
    assert refresh.seconds == 5 * 60
