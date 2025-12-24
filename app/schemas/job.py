from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class JobRequest(BaseModel):
    job_description: str
    resume_id: int | None = None


class JobResult(BaseModel):
    similarity_score: float
    tailored_resume: str
    keywords: list[str]


class JobRead(BaseModel):
    id: int
    content: str
    similarity_score: str | None
    tailored_resume: str | None
    keywords: str | None
    created_at: datetime

    class Config:
        from_attributes = True
