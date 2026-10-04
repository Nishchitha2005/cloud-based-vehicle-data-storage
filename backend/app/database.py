import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Read database URL from environment variables.
# If DATABASE_URL is not available, use SQLite locally.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./vehicle_telemetry.db"
)


# Convert Render/PostgreSQL URLs into the SQLAlchemy psycopg format.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )


# SQLite configuration for local development.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False
        }
    )

# PostgreSQL configuration for production.
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )


# Database session factory.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for SQLAlchemy models.
Base = declarative_base()


# Dependency used by FastAPI endpoints.
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()