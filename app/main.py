import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, resumes, jobs
from app.core.config import settings
from app.db.session import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)


@app.get("/", tags=["health"])
def read_root():
    return {"status": "ok", "message": "Resume Tailoring API is running"}
