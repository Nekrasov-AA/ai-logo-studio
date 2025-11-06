import asyncio, json, uuid
from fastapi import APIRouter, Response
from starlette.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.db import get_session, SessionLocal
from ..models.job import Job

router = APIRouter(prefix="/api", tags=["progress"])

def sse_event(data: dict) -> bytes:
    return f"data: {json.dumps(data)}\n\n".encode("utf-8")

@router.get("/progress/{job_id}")
async def progress_stream(job_id: uuid.UUID):
    async def event_gen():
        # отдельная сессия, чтобы не зависеть от DI
        async with SessionLocal() as session:
            last = None
            while True:
                q = await session.execute(select(Job.status).where(Job.id == job_id))
                row = q.first()
                if not row:
                    yield sse_event({"stage": "not_found"})
                    break
                status = row[0]
                if status != last:
                    last = status
                    yield sse_event({"stage": status})
                if status in ("done", "error"):
                    break
                await asyncio.sleep(0.5)
    return StreamingResponse(
        event_gen(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # для nginx
        }
    )
