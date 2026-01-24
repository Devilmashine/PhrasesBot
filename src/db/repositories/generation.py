from __future__ import annotations

from sqlalchemy import select

from src.db.models import Generation


class GenerationRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def add_generation(self, user_id: int, topic: str, keywords: str, phrases_count: int) -> None:
        async with self.session_factory() as session:
            generation = Generation(
                user_id=user_id,
                topic=topic,
                keywords=keywords,
                phrases_count=phrases_count,
            )
            session.add(generation)
            await session.commit()

    async def last_generations(self, user_id: int, limit: int = 5):
        async with self.session_factory() as session:
            result = await session.execute(
                select(Generation)
                .where(Generation.user_id == user_id)
                .order_by(Generation.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
