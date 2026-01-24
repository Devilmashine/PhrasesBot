from __future__ import annotations

from typing import Iterable

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User


class UserRepository:
    def __init__(self, session_factory):
        """
        session_factory: callable returning AsyncSession (e.g., async_session_maker)
        """
        self.session_factory = session_factory

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        async with self.session_factory() as session:  # type: AsyncSession
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            return result.scalar_one_or_none()

    async def get_or_create(self, tg_id: int, username: str | None = None) -> User:
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            user = result.scalar_one_or_none()
            if user:
                # обновим username если изменился
                if username and user.username != username:
                    user.username = username
                    await session.commit()
                return user

            user = User(tg_id=tg_id, username=username)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def set_ban(self, tg_id: int, is_banned: bool) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(is_banned=is_banned)
            )
            await session.commit()

    async def set_admin(self, tg_id: int, is_admin: bool) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(is_admin=is_admin)
            )
            await session.commit()

    async def list_users(self, limit: int = 20) -> Iterable[User]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).order_by(User.created_at.desc()).limit(limit)
            )
            return result.scalars().all()

    async def stats(self) -> dict:
        async with self.session_factory() as session:
            total = await session.scalar(select(func.count()).select_from(User))
            banned = await session.scalar(
                select(func.count()).select_from(User).where(User.is_banned.is_(True))
            )
            admins = await session.scalar(
                select(func.count()).select_from(User).where(User.is_admin.is_(True))
            )
            return {"total": total or 0, "banned": banned or 0, "admins": admins or 0}
