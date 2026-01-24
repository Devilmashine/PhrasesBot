from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.db.repositories.generation import GenerationRepository

router = Router()


@router.message(Command("account"))
async def account(message: Message, user, generation_repo: GenerationRepository):
    gens = await generation_repo.last_generations(user.id, limit=5)
    if not gens:
        history = "История пока пустая."
    else:
        lines = [
            f"• {g.topic} | {g.keywords} | {g.phrases_count} фраз"
            for g in gens
        ]
        history = "Последние генерации:\n" + "\n".join(lines)

    await message.answer(
        f"Ваш профиль:\n"
        f"ID: {user.tg_id}\n"
        f"Username: @{user.username or '—'}\n\n"
        f"{history}"
    )
