from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📝 Генерировать текст", callback_data="generate_text")],
        [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")],
    ]
)

stop_generation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Остановить генерацию", callback_data="stop_generate_text")]
    ]
)

admin_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_list_users")],
        [
            InlineKeyboardButton(text="🚫 Забанить", callback_data="admin_ban_prompt"),
            InlineKeyboardButton(text="✅ Разбанить", callback_data="admin_unban_prompt"),
        ],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    ]
)
