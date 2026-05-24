import hashlib, hmac, uuid
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from rq import Queue

from app.config import settings
from app.database import get_db
from app.models.orm import Review
from app.services.reviewer import run_review

router = APIRouter()
redis_conn = Redis.from_url(settings.REDIS_URL)
review_queue = Queue("reviews", connection=redis_conn)

def verify_signature(payload: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@router.post("/webhooks/github")
async def github_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")
    
    if not verify_signature(body, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    # Only handle PR open/sync events
    if event != "pull_request":
        return {"status": "ignored"}
    if payload.get("action") not in ("opened", "synchronize"):
        return {"status": "ignored"}

    # after signature verification
    from app.api.config import get_config
    cfg = get_config()
    if cfg.repo and payload["repository"]["full_name"] != cfg.repo: 
        return {"status": "ignored", "reason": "repo not configured"}

    repo = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
    pr_title = payload["pull_request"]["title"]
    pr_author = payload["pull_request"]["user"]["login"]

    # Create review record
    review = Review(
        id=uuid.uuid4(),
        repo_full_name=repo,
        pr_number=pr_number,
        pr_title=pr_title,
        pr_author=pr_author,
        status="pending",
    )
    db.add(review)
    await db.commit()

    # Enqueue async job
    review_queue.enqueue(
        run_review,
        str(review.id),
        repo,
        pr_number,
        settings.GITHUB_TOKEN,
        job_timeout=300,
    )

    return {"status": "queued", "review_id": str(review.id)}
