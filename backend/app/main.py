from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes_generate import router as generate_router
from .core.kafka import init_producer, shutdown_producer
from .api.routes_generate import router as generate_router
from .api.routes_progress import router as progress_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(progress_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
async def _startup():
    await init_producer()

@app.on_event("shutdown")
async def _shutdown():
    await shutdown_producer()

app.include_router(generate_router)

