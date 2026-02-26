import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Option 1: Full DATABASE_URL (password must be URL-encoded if special chars)
    database_url: Optional[str] = os.getenv("DATABASE_URL")

    # Option 2: Separate components (handles special chars automatically)
    db_host: Optional[str] = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_user: Optional[str] = os.getenv("DB_USER")
    db_password: Optional[str] = os.getenv("DB_PASSWORD")
    db_name: Optional[str] = os.getenv("DB_NAME")

    class Config:
        env_file = ".env"


settings = Settings()
