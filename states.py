from aiogram.fsm.state import StatesGroup, State

class Gen(StatesGroup):
    text_prompt = State()
    topic = State()
    keywords = State()
    phrases_num = State()