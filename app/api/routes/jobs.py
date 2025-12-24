from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.job import JobRequest, JobResult
from app.services.job import JobService
from app.services.resume import ResumeService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/analyze", response_model=JobResult)
def analyze_job(
    payload: JobRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    resume_service = ResumeService(db)
    job_service = JobService(db)

    resume = None
    if payload.resume_id:
        resume = resume_service.get_resume(payload.resume_id, current_user.id)
        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found for user")
    else:
        resume = resume_service.latest_resume_for_user(current_user.id)
        if not resume:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a resume first")

    job_record = job_service.analyze(resume, payload.job_description)
    keywords = job_record.keywords.split(", ") if job_record.keywords else []
    return JobResult(
        similarity_score=float(job_record.similarity_score or 0),
        tailored_resume=job_record.tailored_resume or "",
        keywords=keywords,
    )
