from __future__ import annotations

from aiogram import BaseMiddleware


class ContextMiddleware(BaseMiddleware):
    """
    Прокидывает сервисы/репозитории в data, чтобы использовать
    dependency injection aiogram.
    """

    def __init__(self, **context):
        super().__init__()
        self.context = context

    async def __call__(self, handler, event, data):
        data.update(self.context)
        return await handler(event, data)
