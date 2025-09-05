import asyncio
import contextlib
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from ..deps import get_current_user_session
from ..models import User
from ..settings import settings

router = APIRouter()


@router.get("/subscribe")
async def subscribe(
    league_key: str = Query(..., alias="league_key"),
    week: int = Query(..., alias="week"),
    user: User = Depends(get_current_user_session),
) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        channel = f"live:{league_key}:w{week}"
        redis: Redis | None = None
        pubsub: PubSub | None = None
        try:
            try:
                redis = Redis.from_url(settings.redis_url, decode_responses=True)
                await redis.ping()
            except Exception:
                try:
                    import fakeredis.aioredis as fakeredis

                    redis = fakeredis.FakeRedis()
                except Exception:
                    redis = None

            if redis is None:
                while True:
                    yield "event: heartbeat\ndata: ok\n\n"
                    await asyncio.sleep(25)

            pubsub = redis.pubsub()
            await pubsub.subscribe(channel)
            while True:
                message: dict[str, Any] | None = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=25
                )
                if message and message.get("data"):
                    yield f"data: {message['data']}\n\n"
                else:
                    yield "event: heartbeat\ndata: ok\n\n"
        finally:
            if pubsub is not None:
                with contextlib.suppress(Exception):
                    await pubsub.unsubscribe(channel)
                    await pubsub.close()
            if redis is not None:
                with contextlib.suppress(Exception):
                    await redis.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
