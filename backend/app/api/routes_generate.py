from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.db import get_session
from ..core.kafka import get_producer
from ..core.s3 import presigned_get_url
from ..models.job import Job
from ..schemas.job import JobCreate, JobCreated

router = APIRouter(prefix="/api", tags=["generate"])

@router.post("/generate", response_model=JobCreated)
async def create_job(payload: JobCreate, session: AsyncSession = Depends(get_session)):
    job = Job(business_type=payload.business_type, prefs=payload.preferences, status="queued")
    session.add(job)
    await session.commit()
    await session.refresh(job)

    msg = {
        "job_id": str(job.id),
        "user_id": None,
        "business_type": job.business_type,
        "prefs": job.prefs,
    }
    producer = get_producer()
    await producer.send_and_wait("logo.requests", msg)

    return JobCreated(job_id=str(job.id), status=job.status)

@router.get("/result/{job_id}")
async def get_result(job_id: str, session: AsyncSession = Depends(get_session)):
    q = await session.execute(select(Job).where(Job.id == job_id))
    job: Job | None = q.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.result_svg_key:
        return {
            "job_id": str(job.id),
            "status": job.status,
            "svg": {
                "s3_key": job.result_svg_key,
                "url": presigned_get_url(job.result_svg_key, 3600),
            },
        }
    return {"job_id": str(job.id), "status": job.status, "svg": None}
