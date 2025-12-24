import os
from pathlib import Path
from typing import Optional

import pdfplumber
from docx import Document
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.resume import Resume


class ResumeService:
    def __init__(self, db: Session):
        self.db = db
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    def _save_file(self, file: UploadFile) -> str:
        file_location = Path(settings.UPLOAD_DIR) / file.filename
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())
        return str(file_location)

    def _parse_pdf(self, path: str) -> str:
        with pdfplumber.open(path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text

    def _parse_docx(self, path: str) -> str:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    def parse_resume(self, file: UploadFile, user_id: int) -> Resume:
        saved_path = self._save_file(file)
        ext = os.path.splitext(saved_path)[1].lower()
        if ext == ".pdf":
            content = self._parse_pdf(saved_path)
        elif ext in {".doc", ".docx"}:
            content = self._parse_docx(saved_path)
        else:
            raise ValueError("Unsupported file type. Please upload PDF or DOCX.")

        resume = Resume(user_id=user_id, file_path=saved_path, content=content)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get_resume(self, resume_id: int, user_id: int) -> Optional[Resume]:
        return self.db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()

    def latest_resume_for_user(self, user_id: int) -> Optional[Resume]:
        return (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .first()
        )
