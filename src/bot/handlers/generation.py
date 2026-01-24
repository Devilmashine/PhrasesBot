from __future__ import annotations

import asyncio
import os
from pathlib import Path

from aiogram import F, Router, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from src.bot.keyboards import inline as kb_inline
from src.bot.states import GenerationState
from src.core import texts
from src.db.repositories.generation import GenerationRepository
from src.services.openai_service import OpenAIService, UnsupportedRegionError

router = Router()
OUTPUT_FILE = Path("generated_phrases.txt")


@router.callback_query(F.data == "generate_text")
async def input_text_prompt(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(stop_exec_flag=False)
    await state.set_state(GenerationState.topic)
    await callback.message.edit_text(texts.gen_text)
    await callback.message.answer("Введите тему:")
    await callback.answer()


@router.message(GenerationState.topic)
async def collect_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text, stop_exec_flag=False)
    await state.set_state(GenerationState.keywords)
    await message.answer("Введите ключевые слова:")


@router.message(GenerationState.keywords)
async def collect_keywords(message: Message, state: FSMContext):
    await state.update_data(keywords=message.text)
    await state.set_state(GenerationState.phrases_num)
    await message.answer("Введите количество фраз:")


@router.message(GenerationState.phrases_num)
@flags.chat_action("typing")
async def generate_phrases(
    message: Message,
    state: FSMContext,
    openai_service: OpenAIService,
    generation_repo: GenerationRepository,
    user,
):
    raw = message.text
    try:
        phrases_num = int(raw)
        if phrases_num <= 0 or phrases_num > 1000:
            raise ValueError
    except ValueError:
        await message.answer("Количество фраз должно быть целым числом от 1 до 1000.")
        return

    data = await state.get_data()
    topic = data.get("topic")
    keywords = data.get("keywords")

    wait_msg = await message.answer(texts.gen_wait, reply_markup=kb_inline.stop_generation_keyboard)

    async def stop_check():
        current = await state.get_data()
        return current.get("stop_exec_flag", False)

    try:
        phrases = await openai_service.generate_phrases(
            topic=topic, keywords=keywords, count=phrases_num, stop_check=stop_check
        )
    except UnsupportedRegionError:
        await wait_msg.edit_text(
            "OpenAI вернул ошибку региона. Попробуйте другой ключ или прокси."
        )
        await state.clear()
        return
    except Exception:
        await wait_msg.edit_text(texts.gen_error)
        await state.clear()
        return

    if not phrases:
        await wait_msg.edit_text(texts.gen_error)
        await state.clear()
        return

    # запись результата
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for line in phrases:
            f.write(line + os.linesep)

    await wait_msg.answer_document(
        document=FSInputFile(OUTPUT_FILE, filename=OUTPUT_FILE.name),
        caption="Готово!",
    )

    # сохранить в истории
    await generation_repo.add_generation(
        user_id=user.id, topic=topic or "", keywords=keywords or "", phrases_count=len(phrases)
    )

    # удалить временный файл
    if OUTPUT_FILE.exists():
        try:
            OUTPUT_FILE.unlink()
        except OSError:
            pass

    await state.clear()


@router.callback_query(F.data == "stop_generate_text")
async def stop_generation(callback: CallbackQuery, state: FSMContext):
    await state.update_data(stop_exec_flag=True)
    await callback.answer("Генерация остановлена", show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=kb_inline.menu_keyboard)
