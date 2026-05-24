from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class FindingOut(BaseModel):
    id: UUID
    category: str
    severity: str
    file_path: str
    line_number: int | None
    message: str
    suggestion: str

    class Config:
        from_attributes = True

class ReviewOut(BaseModel):
    id: UUID
    repo_full_name: str
    pr_number: int
    pr_title: str
    pr_author: str
    status: str
    summary: str | None
    created_at: datetime
    completed_at: datetime | None
    findings: list[FindingOut] = []

    class Config:
        from_attributes = True
