"""Friday Studio — Server-Sent Events for real-time updates."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.worker import event_queues

router = APIRouter(tags=["sse"])


@router.get("/projects/{project_id}/events")
async def api_project_events(project_id: str):
    queue = event_queues.setdefault(project_id, asyncio.Queue())

    async def event_generator():
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
