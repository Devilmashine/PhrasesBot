from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.core import texts


class AuthMiddleware(BaseMiddleware):
    """
    Проверяет наличие пользователя в БД, создаёт при первом обращении.
    Блокирует забаненных пользователей.
    """

    def __init__(self, user_repo, admin_ids: list[int]):
        super().__init__()
        self.user_repo = user_repo
        self.admin_ids = set(admin_ids or [])

    async def __call__(self, handler, event, data):
        user_obj = None
        from_user = getattr(event, "from_user", None)

        if from_user:
            user_obj = await self.user_repo.get_or_create(
                tg_id=from_user.id, username=from_user.username
            )

            # начальный список админов из env
            if from_user.id in self.admin_ids and not user_obj.is_admin:
                await self.user_repo.set_admin(from_user.id, True)
                user_obj.is_admin = True

            if user_obj.is_banned:
                await self._reply_blocked(event)
                return

        if user_obj:
            data["user"] = user_obj

        return await handler(event, data)

    @staticmethod
    async def _reply_blocked(event: Message | CallbackQuery):
        if isinstance(event, CallbackQuery):
            await event.answer(texts.ban_message, show_alert=True)
        else:
            await event.answer(texts.ban_message)
