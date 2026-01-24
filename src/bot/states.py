from aiogram.fsm.state import State, StatesGroup


class GenerationState(StatesGroup):
    topic = State()
    keywords = State()
    phrases_num = State()


class AdminPromptState(StatesGroup):
    ban_user = State()
    unban_user = State()
