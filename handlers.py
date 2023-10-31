import asyncio
import logging
import os
import re
import time
from aiogram import F, Bot, Router, flags
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
import key_word_generator
from states import Gen
import kb
import text
import config

router = Router()
bot = Bot(token=config.BOT_TOKEN)

async def stop_execution(state: FSMContext):
    await state.update_data({"stop_exec_flag": True})

@router.message(Command("start"))
async def start_handler(msg: Message):
    """Handle the start command."""
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)

@router.message(F.text=="Меню")
@router.message(F.text=="Выйти в меню")
@router.message(F.text=="◀️ Выйти в меню")
async def menu(msg: Message):
    """Handle the menu command."""
    await msg.answer(text.menu, reply_markup=kb.menu)

@router.callback_query(F.data == "generate_text")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    """Start the text generation task."""
    await state.set_state(Gen.text_prompt_input)
    await clbck.message.edit_text(text.gen_text)
    await clbck.message.answer("Введите тему:")
    await state.set_data({"input_type": "topic"})

@router.message(Gen.text_prompt_input)
@flags.chat_action("typing")
async def collect_user_input(msg: Message, state: FSMContext) -> None:
    """Collect the user's input for the text generation task."""
    input_type = (await state.get_data()).get("input_type", None)
    if input_type == "topic":
        await state.update_data({"topic": msg.text})
        await msg.reply("Введите ключевые слова:")
        await state.update_data({"input_type": "keywords"})
        return
    if input_type == "keywords":
        await state.update_data({"keywords": msg.text})
        await msg.reply("Введите количество фраз:")
        await state.update_data({"input_type": "phrases_num"})
        return
    if input_type == "phrases_num":
        phrases_num: int = int(msg.text)
        # Validate the user's input
        if not isinstance(phrases_num, int) or phrases_num <= 0:
            await msg.reply("Количество фраз должно быть положительным целым числом.")
            return
    try:
        data = await state.get_data()  # Get the stored data
        topic = data.get("topic")
        keywords = data.get("keywords")
        mesg = await msg.answer(text.gen_wait, reply_markup=kb.stop_menu)
        await gen_text(
            topic,
            keywords,
            phrases_num,
            state
        )
    except Exception as e:
        logging.error(e)
        await msg.reply('Ошибка генерации фраз')
        return
    else:
        if not (await state.get_data()).get("stop_exec_flag"):
            await mesg.answer_document(document=FSInputFile("generated_phrases.txt", filename="generated_phrases.txt"), caption="Готово!" )
            file_path = "generated_phrases.txt"
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            return
    await state.clear()

@router.callback_query(F.data == "stop_generate_text")
async def stop_gen_text(clbck: CallbackQuery, state: FSMContext):
    """Stop the text generation task."""
    await state.update_data({"stop_exec_flag": True})
    await clbck.message.edit_text("Генерация остановлена. Нажми /start, чтобы начать новую генерацию.")
    
async def gen_text(topic: str, keywords: str, phrases_num: int, state) -> str:

    output_file = open("generated_phrases.txt", "w")  # Create a file to store the generated phrases
    output_summary = []
    system_message = "I want you to act as a SEO semantic core phrase generator.\nI want you to answer only with JSON array format. No keys, just array!\nDo not provide explanations.\n\nYou will be provided with a topic and keywords, and your task is to generate 500 low-frequency key phrases only for that topic. \nIn each phrase must be from 4 to 12 words, and from 12 to 120 symbols."
    user_message = f"Topic: {topic}.\nKeywords: {keywords}."
    first_prompt = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
    
    while len(output_summary) < phrases_num and not (await state.get_data()).get("stop_exec_flag"):
        start_time = time.monotonic()
        response = await key_word_generator.main(first_prompt)
        if response:
            output_summary.extend(response)
            for item in response:
                wordList = re.findall(r'\b\w+\b', item)
                count_symbols = len(item)
                if 12 >= len(wordList) >= 4 and 120 >= count_symbols >= 12:
                    output_file.write(item.strip(" \'\"\{\}[].,") + "\n")
            logging.info("ChatGPT сгенерировал: {} фраз".format(len(output_summary)))
        end_time = time.monotonic()
        iteration_time = end_time - start_time
        if iteration_time < 20:
            await asyncio.sleep(iteration_time)  # Пауза между запросами
    output_file.close()
    return