from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from redis import Redis
from app.config import settings
import httpx
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/config")
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

SUPPORTED_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

class AppConfig(BaseModel):
    repo: str = ""
    model: str = "llama-3.3-70b-versatile"

def get_config() -> AppConfig:
    raw = redis.get("app:config")
    if raw:
        return AppConfig(**json.loads(raw))
    return AppConfig()

async def register_webhook(repo: str):
    if not settings.PUBLIC_URL:
        logger.warning("PUBLIC_URL not set — skipping webhook registration")
        return

    if not settings.GITHUB_TOKEN:
        logger.warning("GITHUB_TOKEN not set — skipping webhook registration")
        return

    webhook_url = f"{settings.PUBLIC_URL}/webhooks/github"

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"https://api.github.com/repos/{repo}/hooks",
            headers={
                "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={
                "name": "web",
                "active": True,
                "events": ["pull_request"],
                "config": {
                    "url": webhook_url,
                    "content_type": "json",
                    "secret": settings.GITHUB_WEBHOOK_SECRET,
                    "insecure_ssl": "0",
                },
            }
        )

    if r.status_code == 201:
        logger.info(f"Webhook registered on {repo}")
    elif r.status_code == 422:
        logger.info(f"Webhook already exists on {repo} — skipping")
    elif r.status_code == 404:
        logger.error(f"Repo {repo} not found or token lacks access")
    else:
        logger.error(f"Webhook registration failed [{r.status_code}]: {r.text}")

@router.get("/", response_model=AppConfig)
async def read_config():
    return get_config()

@router.put("/", response_model=AppConfig)
async def update_config(cfg: AppConfig, background_tasks: BackgroundTasks):
    # Load previous config to check if repo changed
    prev = get_config()

    redis.set("app:config", cfg.model_dump_json())

    # Only register webhook if repo was changed and is non-empty
    if cfg.repo and cfg.repo != prev.repo:
        background_tasks.add_task(register_webhook, cfg.repo)
        logger.info(f"Queued webhook registration for {cfg.repo}")

    return cfg

@router.get("/models")
async def list_models():
    return {"models": SUPPORTED_MODELS}

@router.get("/status")
async def config_status():
    cfg = get_config()
    return {
        "repo": cfg.repo,
        "model": cfg.model,
        "public_url": settings.PUBLIC_URL,
        "webhook_target": f"{settings.PUBLIC_URL}/webhooks/github" if settings.PUBLIC_URL else None,
    }
