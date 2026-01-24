from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

engine = create_async_engine(settings.sqlalchemy_url, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    return async_session_maker()


async def init_models(Base) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
