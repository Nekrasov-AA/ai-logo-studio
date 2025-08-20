from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.db import get_session
from ..models.job import Job
from ..schemas.job import JobCreate, JobCreated
from ..core.kafka import get_producer

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
