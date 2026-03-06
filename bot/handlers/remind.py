import logging
from datetime import datetime

from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext

from bot.database.db import get_db
from bot.states import Form
from bot.database.repository import ReminderRepository

remind_router = Router(name="remind")

logger = logging.getLogger(__name__)

@remind_router.message(Command("remind"))
async def remind(message: types.Message, state: FSMContext):
    await message.answer("О чём нужно напомнить?")
    logger.info("Вызвана команда remind")
    await state.set_state(Form.waiting_for_remind)


@remind_router.message(Form.waiting_for_remind)
async def process_text(message: types.Message, state: FSMContext):
    logger.info("Пользователь ввёл текст")
    await state.update_data(text=message.text)
    await message.answer("Введи дату (например 25.12.2025 18:00):")
    await state.set_state(Form.waiting_for_date)

@remind_router.message(Form.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    data = await state.get_data()
    text = data["text"]
    date = message.text
    try:
        date = datetime.strptime(date, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer("Неправильно указана дата, введите дату в формате 25.12.2025 18:00")
        return

    db = get_db()
    session = db.get_session()
    reminder = ReminderRepository(session)
    try:
        await reminder.create(
            text=text,
            remind_at=date,
            user_id=user_id
        )
        logger.info("Напоминание создано")
    except Exception as e:
        logger.info(f"Failed to create reminder: {e}")

    await message.answer("Напоминание успешно создано!")
    await state.set_state(Form.base_state)