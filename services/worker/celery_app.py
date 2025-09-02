from datetime import timedelta
import os

from celery import Celery  # type: ignore
from celery.schedules import crontab

BROKER = os.getenv("REDIS_URL", "rediss://redis:6379/0")
BACKEND = BROKER
celery = Celery("edge", broker=BROKER, backend=BACKEND)
celery.conf.task_routes = {"tasks.*": {"queue": "default"}}


def _crontab_from_env(env_name: str, default: str) -> crontab:
    """Parse a cron expression from an env var into a Celery crontab."""

    expr = os.getenv(env_name, default).split()
    if len(expr) != 5:
        raise ValueError(f"{env_name} must be a 5-field cron expression")
    minute, hour, day_of_month, month_of_year, day_of_week = expr
    return crontab(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
        day_of_week=day_of_week,
    )


celery.conf.beat_schedule = {
    "nightly-sync": {
        "task": "tasks.project_week",
        "schedule": _crontab_from_env("NIGHTLY_SYNC_CRON", "0 3 * * *"),
        "args": (1,),
    },
    "tuesday-waivers": {
        "task": "tasks.waiver_shortlist",
        "schedule": _crontab_from_env("WAIVER_SHORTLIST_CRON", "0 9 * * TUE"),
        "args": (528886, 1, 1),
    },
    "gameday-refresh": {
        "task": "tasks.ping",
        "schedule": timedelta(
            minutes=int(os.getenv("GAMEDAY_REFRESH_MINUTES", "10"))
        ),
    },
}
