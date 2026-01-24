from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

exit_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]],
    resize_keyboard=True,
)
