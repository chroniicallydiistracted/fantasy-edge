from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()


@router.get("/subscribe")
async def subscribe() -> StreamingResponse:
    async def event_stream():
        while True:
            yield "event: heartbeat\ndata: ok\n\n"
            await asyncio.sleep(25)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
