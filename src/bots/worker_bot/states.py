from aiogram.fsm.state import State, StatesGroup


class RedeemCoupon(StatesGroup):
    waiting_for_code = State()
    waiting_for_amount = State()
