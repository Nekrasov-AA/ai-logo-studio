from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from .api.routes_generate import router as generate_router
from .api.routes_progress import router as progress_router
from .core.kafka import init_producer, shutdown_producer
from .core.s3 import ensure_bucket
from .core.metrics import get_prometheus_metrics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",  # Vite dev server default
        "http://127.0.0.1:5173"   # Vite dev server default
    ],
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(progress_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    data = await get_prometheus_metrics()
    return Response(content=data, media_type="text/plain")

@app.on_event("startup")
async def _startup():
    await init_producer()
    ensure_bucket()  # Ensure S3 bucket exists

@app.on_event("shutdown")
async def _shutdown():
    await shutdown_producer()

