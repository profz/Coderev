import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    repo_full_name: Mapped[str] = mapped_column(String)
    pr_number: Mapped[int] = mapped_column(Integer)
    pr_title: Mapped[str] = mapped_column(String)
    pr_author: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        Enum("pending", "processing", "completed", "failed", name="review_status"),
        default="pending"
    )
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    findings: Mapped[list["Finding"]] = relationship(back_populates="review")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("reviews.id"))
    category: Mapped[str] = mapped_column(String)   # bug | security | performance | smell
    severity: Mapped[str] = mapped_column(String)   # critical | high | medium | low
    file_path: Mapped[str] = mapped_column(String)
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message: Mapped[str] = mapped_column(String)
    suggestion: Mapped[str] = mapped_column(String)

    review: Mapped["Review"] = relationship(back_populates="findings")
