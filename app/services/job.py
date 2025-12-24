from typing import Iterable, Optional
from sqlalchemy.orm import Session

from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.services import nlp


class JobService:
    def __init__(self, db: Session):
        self.db = db

    def analyze(self, resume: Resume, job_text: str) -> JobDescription:
        keywords = nlp.extract_keywords(job_text)
        similarity = nlp.compute_similarity(resume.content, job_text)
        tailored_resume = nlp.enhance_bullets(resume.content, keywords)

        job_record = JobDescription(
            user_id=resume.user_id,
            content=job_text,
            similarity_score=f"{similarity:.4f}",
            tailored_resume=tailored_resume,
            keywords=", ".join(keywords),
        )
        self.db.add(job_record)
        self.db.commit()
        self.db.refresh(job_record)
        return job_record

    def keywords_from_text(self, text: str, limit: int = 20) -> Iterable[str]:
        return nlp.extract_keywords(text, limit=limit)

    def latest_for_user(self, user_id: int) -> Optional[JobDescription]:
        return (
            self.db.query(JobDescription)
            .filter(JobDescription.user_id == user_id)
            .order_by(JobDescription.created_at.desc())
            .first()
        )
