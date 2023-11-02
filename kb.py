from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

menu = [
    [InlineKeyboardButton(text="📝 Генерировать текст", callback_data="generate_text")],
#    [InlineKeyboardButton(text="💳 Купить токены", callback_data="buy_tokens"),
#    InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
#    [InlineKeyboardButton(text="💎 Партнёрская программа", callback_data="ref"),
#    InlineKeyboardButton(text="🎁 Бесплатные токены", callback_data="free_tokens")],
    [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]
]

stop_menu = [
    [InlineKeyboardButton(text="Остановить генерацию", callback_data="stop_generate_text")]
]

#main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
#main_admin.add('◀️ Выйти в меню').add('Админ-панель')

menu = InlineKeyboardMarkup(inline_keyboard=menu)
stop_menu = InlineKeyboardMarkup(inline_keyboard=stop_menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])

