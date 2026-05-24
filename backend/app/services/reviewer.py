from app.agents.graph import review_graph
from app.database import AsyncSessionLocal
from app.models.orm import Review, Finding
from datetime import datetime
import uuid

async def run_review(review_id: str, repo: str, pr_number: int, token: str):
    async with AsyncSessionLocal() as db:
        review = await db.get(Review, uuid.UUID(review_id))
        review.status = "processing"
        await db.commit()

    initial_state = {
        "repo_full_name": repo,
        "pr_number": pr_number,
        "installation_token": token,
        "findings": [],
        "error": None,
        # pre-fill keys fetcher will overwrite
        "pr_title": "",
        "pr_author": "",
        "diff": "",
        "changed_files": [],
        "summary": "",
        "review_id": review_id,
    }

    try:
        result = await review_graph.ainvoke(initial_state)

        async with AsyncSessionLocal() as db:
            review = await db.get(Review, uuid.UUID(review_id))
            review.status = "completed"
            review.summary = result.get("summary")
            review.pr_title = result.get("pr_title", "")
            review.pr_author = result.get("pr_author", "")
            review.completed_at = datetime.utcnow()

            for f in result.get("findings", []):
                db.add(Finding(
                    review_id=review.id,
                    category=f["category"],
                    severity=f["severity"],
                    file_path=f["file_path"],
                    line_number=f.get("line_number"),
                    message=f["message"],
                    suggestion=f["suggestion"],
                ))
            await db.commit()

    except Exception as e:
        async with AsyncSessionLocal() as db:
            review = await db.get(Review, uuid.UUID(review_id))
            review.status = "failed"
            await db.commit()
        raise e
