from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    base_state = State()
    waiting_for_remind = State()
    waiting_for_date = State()