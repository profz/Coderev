from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    APP_ENV: str = "development"

    GITHUB_TOKEN: str
    GITHUB_WEBHOOK_SECRET: str

    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    REDIS_URL: str = "redis://localhost:6379"
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/codereview"

    PUBLIC_URL: str = ""   # e.g. https://xxxx.serveousercontent.com

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
    )

settings = Settings()
