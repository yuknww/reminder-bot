import logging
from datetime import datetime, timedelta

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.database.db import get_db
from bot.database.repository import ReminderRepository
from bot.states import Form

remind_router = Router(name="remind")

logger = logging.getLogger(__name__)


@remind_router.message(Command("remind"))
async def remind(message: types.Message, state: FSMContext):
    logger.info("User %s called /remind", message.from_user.id)
    await message.answer(
        "✨ О чём тебе напомнить?\n\n"
        "Напиши текст напоминания, например:\n"
        "«Позвонить родителям» или «Сходить в спортзал» 💪"
    )
    await state.set_state(Form.waiting_for_remind)


@remind_router.message(Form.waiting_for_remind)
async def process_text(message: types.Message, state: FSMContext):
    logger.info("User %s entered reminder text", message.from_user.id)
    await state.update_data(text=message.text)
    await message.answer(
        "🗓 Теперь введи дату и время, когда напомнить.\n\n"
        "Формат: 25.12.2025 18:00\n"
        "То есть: ДД.ММ.ГГГГ ЧЧ:ММ ⏰"
    )
    await state.set_state(Form.waiting_for_date)


@remind_router.message(Form.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    data = await state.get_data()
    text = data.get("text")
    raw_date = message.text

    logger.info("User %s entered date '%s' for reminder", user_id, raw_date)

    try:
        remind_at = datetime.strptime(raw_date, "%d.%m.%Y %H:%M")
    except ValueError:
        logger.warning(
            "User %s provided invalid date format: %s",
            user_id,
            raw_date,
        )
        await message.answer(
            "⚠️ Не получилось разобрать дату.\n\n"
            "Пожалуйста, введи в формате: 25.12.2025 18:00 ⏰"
        )
        return

    # Проверка, что дата в будущем
    now = datetime.now()
    if remind_at <= now:
        logger.warning(
            "User %s provided past date: %s (now: %s)",
            user_id,
            remind_at,
            now,
        )
        await message.answer(
            "⏳ Дата уже в прошлом.\n\n"
            "Укажи время, которое ещё не прошло, например: 25.12.2025 18:00 😊"
        )
        return

    db = get_db()
    session = db.get_session()
    repository = ReminderRepository(session)

    try:
        reminder = await repository.create(
            text=text,
            remind_at=remind_at,
            user_id=user_id,
        )
        logger.info("Reminder %s created for user %s", reminder.id, user_id)
        await message.answer(
            "✅ Готово! Я обязательно напомню тебе в нужный момент ✨"
        )
    except Exception as e:
        logger.error("Failed to create reminder for user %s: %s", user_id, e)
        await message.answer(
            "😔 Не удалось создать напоминание.\n"
            "Попробуй, пожалуйста, ещё раз чуть позже."
        )

    await state.set_state(Form.base_state)