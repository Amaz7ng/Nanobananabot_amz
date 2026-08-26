from aiogram.fsm.state import State, StatesGroup

class GenerateState(StatesGroup):
    waiting_for_style = State()
    waiting_for_prompt = State()