import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware

from src.bot.handlers import admin, generation, start, user
from src.bot.middlewares.auth import AuthMiddleware
from src.bot.middlewares.context import ContextMiddleware
from src.core.config import settings
from src.db.database import async_session_maker, init_models
from src.db.models import Base
from src.db.repositories.generation import GenerationRepository
from src.db.repositories.user import UserRepository
from src.services.openai_service import OpenAIService


async def main():
    logging.basicConfig(level=logging.INFO)

    await init_models(Base)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    openai_service = OpenAIService(settings.openai_keys)
    user_repo = UserRepository(async_session_maker)
    generation_repo = GenerationRepository(async_session_maker)

    shared_context = dict(
        openai_service=openai_service,
        user_repo=user_repo,
        generation_repo=generation_repo,
        settings=settings,
    )

    # порядок: контекст -> auth -> chat action
    dp.message.middleware(ContextMiddleware(**shared_context))
    dp.callback_query.middleware(ContextMiddleware(**shared_context))

    dp.message.middleware(AuthMiddleware(user_repo, settings.admin_id_list))
    dp.callback_query.middleware(AuthMiddleware(user_repo, settings.admin_id_list))

    dp.message.middleware(ChatActionMiddleware())
    dp.callback_query.middleware(ChatActionMiddleware())

    dp.include_routers(
        start.router,
        generation.router,
        admin.router,
        user.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")