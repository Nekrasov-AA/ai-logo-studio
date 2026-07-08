import asyncio
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.db import SessionLocal, get_session
from ..models.job import Job
from ..models.variant import LogoVariant
from ..schemas.job import JobCreate, JobCreated
from ..services.logo_generator import generate_logo_variants

router = APIRouter(prefix="/api", tags=["generate"])


async def _run_generation(
    job_id: uuid.UUID,
    business_name: str,
    business_type: str,
    prefs: dict,
) -> None:
    async with SessionLocal() as session:
        try:
            variants = await asyncio.to_thread(
                generate_logo_variants,
                business_name=business_name,
                business_type=business_type,
                prefs=prefs,
            )
            for i, v in enumerate(variants):
                lv = LogoVariant(
                    job_id=job_id,
                    index=i,
                    palette={
                        "colors": v.palette,
                        "icon": v.icon_name,
                        "font_heading": v.font_heading,
                        "font_body": v.font_body,
                        "layout": v.layout,
                    },
                    svg_key=v.svg.decode("utf-8"),
                )
                session.add(lv)
            job = await session.get(Job, job_id)
            job.status = "done"
            await session.commit()
        except Exception:
            await session.rollback()
            try:
                job = await session.get(Job, job_id)
                if job:
                    job.status = "failed"
                    await session.commit()
            except Exception:
                pass


@router.post("/generate", response_model=JobCreated)
async def create_job(
    payload: JobCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    prefs = payload.preferences
    business_name = str(prefs.get("business_name") or payload.business_type)

    job = Job(business_type=payload.business_type, prefs=prefs, status="processing")
    session.add(job)
    await session.commit()
    await session.refresh(job)

    background_tasks.add_task(
        _run_generation,
        job.id,
        business_name,
        payload.business_type,
        prefs,
    )

    return JobCreated(job_id=str(job.id), status=job.status)


@router.get("/result/{job_id}")
async def get_result(job_id: str, session: AsyncSession = Depends(get_session)):
    q = await session.execute(select(Job).where(Job.id == job_id))
    job = q.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    qv = await session.execute(
        select(LogoVariant).where(LogoVariant.job_id == job.id).order_by(LogoVariant.index)
    )
    variants = qv.scalars().all()

    return {
        "job_id": str(job.id),
        "status": job.status,
        "variants": [
            {
                "index": v.index,
                "palette": v.palette,
                "svg": {
                    "s3_key": f"local:{job.id}:{v.index}",
                    "url": f"/api/svg/{job.id}/{v.index}",
                },
            }
            for v in variants
        ],
    }


@router.get("/svg/{job_id}/{index}")
async def get_svg(
    job_id: str,
    index: int,
    session: AsyncSession = Depends(get_session),
):
    q = await session.execute(
        select(LogoVariant).where(
            LogoVariant.job_id == job_id,
            LogoVariant.index == index,
        )
    )
    variant = q.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="variant not found")
    return Response(content=variant.svg_key, media_type="image/svg+xml")
