from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from app.config import settings

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for Celery workers
sync_engine = create_engine(
    settings.sync_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
)

# Base for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
