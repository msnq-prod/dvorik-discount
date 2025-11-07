from aiogram.fsm.state import State, StatesGroup


class RegisterClient(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_birth_date = State()
    waiting_for_gender = State()
