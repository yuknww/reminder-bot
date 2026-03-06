from aiogram import types
from aiogram.filters import Command
from aiogram import Router

start_router = Router(name="start")

@start_router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет, это бот для напоминаний")