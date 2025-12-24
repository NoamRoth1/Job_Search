from datetime import datetime
from pydantic import BaseModel


class ResumeRead(BaseModel):
    id: int
    file_path: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
