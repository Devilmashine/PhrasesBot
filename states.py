from aiogram.fsm.state import StatesGroup, State

class Gen(StatesGroup):
    text_prompt_input = State()

class StopGen(StatesGroup):
    text_prompt_input = State()