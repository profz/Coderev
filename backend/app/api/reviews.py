from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.orm import Review
from app.models.schemas import ReviewOut
import uuid

router = APIRouter(prefix="/api/reviews")

@router.get("/", response_model=list[ReviewOut])
async def list_reviews(
    skip: int = 0, limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.findings))   # ← eager load
        .order_by(Review.created_at.desc())
        .offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(review_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.findings))   # ← eager load
        .where(Review.id == uuid.UUID(review_id))
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.get("/pr/{pr_number}", response_model=list[ReviewOut])
async def get_reviews_for_pr(pr_number: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.findings))   # ← eager load
        .where(Review.pr_number == pr_number)
    )
    return result.scalars().all()
