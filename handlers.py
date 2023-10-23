import os
from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
import key_word_generator
from states import Gen
import kb
import text
import config

router = Router()
bot = Bot(token=config.BOT_TOKEN)

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)

@router.message(types.ContentType.TEXT(equals=["Меню", "Выйти в меню", "◀️ Выйти в меню"]))
async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)

@router.callback_query(types.ContentType.TEXT(data="generate_text"))
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.text_prompt)
    await clbck.message.edit_text(text.gen_text)
    await clbck.message.answer(text.gen_exit, reply_markup=kb.exit_kb)

async def generate_text(msg: Message, state: FSMContext):
    prompt = msg.text
    await msg.answer(text.gen_wait)
    await Gen.topic.set()
    await state.set_state(Gen.topic)
    await msg.answer("Введите тему:")

@router.message(state=Gen.topic)
async def process_topic(message: types.Message, state: FSMContext):
    topic = message.text
    await state.update_data(topic=topic)
    await Gen.keywords.set()
    await message.reply("Введите ключевые слова:")

@router.message(state=Gen.keywords)
async def process_keywords(message: types.Message, state: FSMContext):
    keywords = message.text
    await state.update_data(keywords=keywords)
    await Gen.phrases_num.set()
    await message.reply("Введите количество фраз:")

@router.message(state=Gen.phrases_num)
async def process_phrases_num(message: types.Message, state: FSMContext):
    phrases_num = int(message.text)
    data = await state.get_data()
    topic = data.get("topic")
    keywords = data.get("keywords")
    try:
        phrases_file = key_word_generator.main(topic, keywords, phrases_num) 
        with open(phrases_file, 'rb') as file:
            await bot.send_document(message.chat.id, file)
        os.unlink(phrases_file)
        await state.finish()
        await message.reply("Готово!")
    except Exception as e:
        await message.reply('Ошибка генерации фраз')
        return