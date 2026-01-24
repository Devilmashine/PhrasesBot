from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.core import texts
from src.bot.keyboards import inline as kb_inline
from src.db.repositories.user import UserRepository

router = Router()


def _is_admin(user) -> bool:
    return bool(user and user.is_admin)


@router.message(Command("admin"))
async def admin_panel(message: Message, user, user_repo: UserRepository):
    if not _is_admin(user):
        await message.answer(texts.no_access)
        return
    stats = await user_repo.stats()
    await message.answer(
        f"Админ-панель.\nВсего пользователей: {stats['total']}\n"
        f"Забанено: {stats['banned']}\nАдминов: {stats['admins']}\n\n"
        "Доступные действия: /ban <tg_id>, /unban <tg_id>, список/статистика кнопками ниже.",
        reply_markup=kb_inline.admin_menu_keyboard,
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, user, user_repo: UserRepository):
    if not _is_admin(user):
        await callback.answer(texts.no_access, show_alert=True)
        return
    stats = await user_repo.stats()
    await callback.message.edit_text(
        f"Статистика:\nВсего пользователей: {stats['total']}\n"
        f"Забанено: {stats['banned']}\nАдминов: {stats['admins']}",
        reply_markup=kb_inline.admin_menu_keyboard,
    )
    await callback.answer()


@router.callback_query(F.data == "admin_list_users")
async def admin_list_users(callback: CallbackQuery, user, user_repo: UserRepository):
    if not _is_admin(user):
        await callback.answer(texts.no_access, show_alert=True)
        return
    users = await user_repo.list_users(limit=20)
    if not users:
        text = "Пользователей пока нет."
    else:
        lines = [
            f"{u.tg_id} @{u.username or '—'} "
            f"{'🚫' if u.is_banned else '✅'} {'(admin)' if u.is_admin else ''}".strip()
            for u in users
        ]
        text = "Последние пользователи:\n" + "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=kb_inline.admin_menu_keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_ban_prompt")
async def admin_ban_prompt(callback: CallbackQuery, user):
    if not _is_admin(user):
        await callback.answer(texts.no_access, show_alert=True)
        return
    await callback.message.edit_text(
        "Чтобы забанить пользователя, отправьте команду: /ban <tg_id>",
        reply_markup=kb_inline.admin_menu_keyboard,
    )
    await callback.answer()


@router.callback_query(F.data == "admin_unban_prompt")
async def admin_unban_prompt(callback: CallbackQuery, user):
    if not _is_admin(user):
        await callback.answer(texts.no_access, show_alert=True)
        return
    await callback.message.edit_text(
        "Чтобы разбанить пользователя, отправьте команду: /unban <tg_id>",
        reply_markup=kb_inline.admin_menu_keyboard,
    )
    await callback.answer()


@router.message(Command("ban"))
async def ban_user(message: Message, user, user_repo: UserRepository):
    if not _is_admin(user):
        await message.answer(texts.no_access)
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Использование: /ban <tg_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("tg_id должен быть числом.")
        return
    await user_repo.set_ban(target_id, True)
    await message.answer(f"Пользователь {target_id} забанен.")


@router.message(Command("unban"))
async def unban_user(message: Message, user, user_repo: UserRepository):
    if not _is_admin(user):
        await message.answer(texts.no_access)
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Использование: /unban <tg_id>")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("tg_id должен быть числом.")
        return
    await user_repo.set_ban(target_id, False)
    await message.answer(f"Пользователь {target_id} разбанен.")
