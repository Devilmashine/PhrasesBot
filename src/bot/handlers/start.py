from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.core import texts
from src.bot.keyboards import inline as kb_inline

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(texts.greet.format(name=message.from_user.full_name), reply_markup=kb_inline.menu_keyboard)


@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu_handler(message: Message):
    await message.answer(texts.menu, reply_markup=kb_inline.menu_keyboard)


@router.callback_query(F.data == "help")
async def help_handler(callback: CallbackQuery):
    await callback.message.edit_text(texts.help_text, reply_markup=kb_inline.menu_keyboard)
    await callback.answer()
