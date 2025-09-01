from celery import Celery
import os

BROKER = os.getenv("REDIS_URL", "redis://redis:6379/0")
BACKEND = BROKER
celery = Celery("edge", broker=BROKER, backend=BACKEND)
celery.conf.task_routes = {"tasks.*": {"queue": "default"}}
