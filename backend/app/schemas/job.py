from pydantic import BaseModel, Field
from typing import Any, Dict

class JobCreate(BaseModel):
    business_type: str
    preferences: Dict[str, Any] = Field(default_factory=dict)

class JobCreated(BaseModel):
    job_id: str
    status: str = "queued"
