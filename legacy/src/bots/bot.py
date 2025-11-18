import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


def get_bot(token: str) -> Bot:
    return Bot(token=token, parse_mode="HTML")


def get_dispatcher() -> Dispatcher:
    storage = MemoryStorage()
    return Dispatcher(storage=storage)


client_bot = get_bot(os.getenv("TELEGRAM_MAIN_BOT_TOKEN", ""))
worker_bot = get_bot(os.getenv("TELEGRAM_AUTH_BOT_TOKEN", ""))

client_dp = get_dispatcher()
worker_dp = get_dispatcher()
