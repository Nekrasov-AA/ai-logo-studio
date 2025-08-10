from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes_generate import router as generate_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(generate_router)
