import os
from aiogram import F, Bot, Router, flags
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from sqlalchemy import Engine
import key_word_generator
from states import Gen
import kb
import text
import config

router = Router()
bot = Bot(token=config.BOT_TOKEN)

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

# ...

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

            mesg = await msg.answer(text.gen_wait)

            doc_info, phrases_file = await key_word_generator.main(
                topic,
                keywords,
                phrases_num
            )

            await mesg.delete()
            await mesg.answer_document(document=FSInputFile("generated_phrases.txt", filename="generated_phrases.txt"), caption=f"Готово! ChatGPT сгенерировал: {doc_info} фраз" )

            os.remove(phrases_file)

        except Exception as e:
            print(e)
            await msg.reply('Ошибка генерации фраз')
            return
