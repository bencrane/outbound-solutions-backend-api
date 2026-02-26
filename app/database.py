from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from app.config import settings


def get_database_url() -> str:
    """Build database URL, handling special chars in password."""
    # If separate components provided, use those (handles special chars)
    if settings.db_host and settings.db_user and settings.db_password:
        encoded_password = quote_plus(settings.db_password)
        return f"postgresql://{settings.db_user}:{encoded_password}@{settings.db_host}:{settings.db_port}/{settings.db_name or 'postgres'}?sslmode=require"

    # Otherwise use DATABASE_URL directly
    if settings.database_url:
        return settings.database_url

    raise ValueError("Database not configured. Set DATABASE_URL or DB_HOST/DB_USER/DB_PASSWORD/DB_NAME")


engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
