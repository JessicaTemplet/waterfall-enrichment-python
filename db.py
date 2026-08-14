import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Defaults to local SQLite; set DATABASE_URL (e.g. postgresql+psycopg://...) for production.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///leadintel.db")

# SQLite needs check_same_thread=False for multi-threaded use (the job worker).
# The connect_args are ignored by other drivers.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()
