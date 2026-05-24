from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import webhook, reviews, health, config
from app.database import engine
from app.models.orm import Base

app = FastAPI(title="AI Code Review", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(reviews.router)
app.include_router(health.router)
app.include_router(config.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
