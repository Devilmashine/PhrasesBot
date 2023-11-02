import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware

from config import config
from handlers import router
from db.db import async_main

async def main():
    await async_main()
    
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ChatActionMiddleware())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")