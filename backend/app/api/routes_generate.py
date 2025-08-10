from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.db import get_session
from ..models.job import Job
from ..schemas.job import JobCreate, JobCreated

router = APIRouter(prefix="/api", tags=["generate"])

@router.post("/generate", response_model=JobCreated)
async def create_job(payload: JobCreate, session: AsyncSession = Depends(get_session)):
    job = Job(business_type=payload.business_type, prefs=payload.preferences, status="queued")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    # On the next step: we will send it to Kafka. For now, we are only saving it to the database.
    return JobCreated(job_id=str(job.id), status=job.status)
