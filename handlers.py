import asyncio
import logging
import os
import re
from dotenv import load_dotenv
from aiogram import F, Bot, Router, flags
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
import key_word_generator
from states import Gen
import kb
import text
from config import config
import db.db as db

router = Router()
bot = Bot(token=config.bot_token.get_secret_value())
load_dotenv(dotenv_path=".env")
OPENAI_TOKENS = os.getenv("OPENAI_TOKENS")
keys = OPENAI_TOKENS.split(",")

async def stop_execution(state: FSMContext):
    await state.update_data({"stop_exec_flag": True})

@router.message(Command("start"))
async def start_handler(msg: Message):
    """Handle the start command."""
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)
"""
    if msg.from_user.id == int(os.getenv('ADMIN_ID')):
        await msg.answer('Вы авторизовались как администратор!', reply_markup=kb.main_admin)

# Функция обработки команды "Регистрация"
@router.message(Command("register"))
async def register_handler(msg: Message):
    # Проверяем, является ли пользователь администратором
    if msg.from_user.id == int(os.getenv('ADMIN_ID')):
        # Отправляем уведомление администратору о регистрации
        await bot.send_message(chat_id=os.getenv('ADMIN_ID'), text="Получена новая заявка на регистрацию")
        # Отправляем сообщение пользователю
        await msg.answer("Заявка находится на рассмотрении администратора")
        # Отправляем кнопки администратору для одобрения или отклонения заявки
        await bot.send_message(chat_id=os.getenv('ADMIN_ID'), text="Выберите действие:", reply_markup=kb.registration_approval)
    else:
        await msg.answer("Вы не являетесь администратором")

# Функция обработки кнопок одобрения или отклонения регистрации
@router.callback_query(F.data == "approve_registration")
async def approve_registration(clbck: CallbackQuery):
    # Получаем данные о пользователе из callback
    user_id = clbck.from_user.id
    user_name = clbck.from_user.full_name
    # Добавляем пользователя в базу данных или выполняем другие действия
    # ...
    # Отправляем уведомление пользователю об одобрении регистрации
    await bot.send_message(chat_id=user_id, text="Ваша заявка на регистрацию одобрена")

@router.callback_query(F.data == "reject_registration")
async def reject_registration(clbck: CallbackQuery):
    # Получаем данные о пользователе из callback
    user_id = clbck.from_user.id
    # Отправляем уведомление пользователю об отклонении регистрации
    await bot.send_message(chat_id=user_id, text="Ваша заявка на регистрацию отклонена")

# Функция обработки команды "Личный кабинет"
@router.message(Command("account"))
async def account_handler(msg: Message):
    # Проверяем, является ли пользователь зарегистрированным
    if is_registered_user(msg.from_user.id):
        # Отправляем пользователю меню личного кабинета
        await msg.answer("Личный кабинет", reply_markup=kb.account_menu)
    else:
        await msg.answer("Вы не зарегистрированы")

# Функция обработки кнопок в личном кабинете
@router.callback_query(F.data == "change_key")
async def change_key(clbck: CallbackQuery):
    # Получаем данные о пользователе из callback
    user_id = clbck.from_user.id
    # Отправляем сообщение пользователю с инструкцией по изменению ключа
    await bot.send_message(chat_id=user_id, text="Введите новый ключ доступа")

@router.callback_query(F.data == "delete_account")
async def delete_account(clbck: CallbackQuery):
    # Получаем данные о пользователе из callback
    user_id = clbck.from_user.id
    # Удаляем пользователя из базы данных или выполняем другие действия
    # ...
    # Отправляем уведомление пользователю об удалении аккаунта
    await bot.send_message(chat_id=user_id, text="Ваш аккаунт удален")
    # Перенаправляем пользователя в главное меню
    await bot.send_message(chat_id=user_id, text="Вы были выведены в главное меню", reply_markup=kb.menu)

# Функция обработки команды "Админ-панель"
@router.message(Command("admin_panel"))
async def admin_panel_handler(msg: Message):
    # Проверяем, является ли пользователь администратором
    if msg.from_user.id == int(os.getenv('ADMIN_ID')):
        # Отправляем администратору меню админ-панели
        await msg.answer("Админ-панель", reply_markup=kb.admin_panel_menu)
    else:
        await msg.answer("Вы не являетесь администратором")

@router.callback_query(F.data == "ban_user")
async def ban_user(clbck: CallbackQuery):
    # Получаем данные о пользователе из callback
    user_id = clbck.data.get("user_id")
    # Баним пользователя или выполняем другие действия
    # ...
    # Отправляем уведомление администратору об успешном бане
    await bot.send_message(chat_id=os.getenv('ADMIN_ID'), text=f"Пользователь {user_id} заблокирован")
"""
    
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
            await mesg.answer_document(document=FSInputFile("generated_phrases.txt", filename="generated_phrases.txt"), caption="Готово!")
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

# Хэндлер без фильтра, сработает, если ни один выше не сработает.
@router.message()
async def echo(message: Message):
    await message.answer('Я тебя не понимаю...')

async def gen_text(topic: str, keywords: str, phrases_num: int, state) -> str:
    output_summary = []
    system_message = "I want you to act as a SEO semantic core phrase generator.\nI want you to answer only with JSON array format. No keys, just array!\nDo not provide explanations.\n\nYou will be provided with a topic and keywords, and your task is to generate 500 low-frequency key phrases only for that topic. \nIn each phrase must be from 4 to 12 words, and from 12 to 120 symbols."
    user_message = f"Topic: {topic}.\nKeywords: {keywords}."

    first_prompt = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    async def generate_phrases(key):
        while len(output_summary) < phrases_num and not (await state.get_data()).get("stop_exec_flag"):
            response = await key_word_generator.main(first_prompt, key)
            if response:
                output_summary.extend(response)
                for item in response:
                    wordList = re.findall(r'\b\w+\b', item)
                    count_symbols = len(item)
                    if 12 >= len(wordList) >= 4 and 120 >= count_symbols >= 12:
                        with open("generated_phrases.txt", "a") as output_file:
                            translation_table = str.maketrans("", "", " \'\"{}[].,")
                            output_file.write(item.translate(translation_table) + "\n")
                logging.info("ChatGPT сгенерировал: {} фраз".format(len(output_summary)))

    # Create a list of tasks to run concurrently
    tasks = [generate_phrases(key) for key in keys]
    
    await asyncio.gather(*tasks)
    return None
