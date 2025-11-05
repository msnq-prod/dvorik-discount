from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

def _create_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, future=True)

engine: AsyncEngine = _create_engine(settings.DB_URL)
SessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None, None]:
    db: AsyncSession = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
