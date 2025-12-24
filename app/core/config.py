import os
from datetime import timedelta


class Settings:
    PROJECT_NAME: str = "Resume Tailoring API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./resume_tailor.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    def access_token_expires(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)


settings = Settings()
