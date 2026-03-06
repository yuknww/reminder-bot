import logging

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.database.db import get_db
from bot.database.repository import ReminderRepository
from bot.states import Form
from bot.database.models import Reminder

start_router = Router(name="start")

logger = logging.getLogger(__name__)

MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Создать напоминание")],
        [KeyboardButton(text="📋 Мои напоминания")],
    ],
    resize_keyboard=True,
)


@start_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    logger.info("User %s called /start", message.from_user.id)
    await state.set_state(Form.base_state)
    await message.answer(
        "Привет 👋\n\n"
        "Я бот-напоминалка и помогу тебе ничего не забыть ✅\n\n"
        "Используй кнопки ниже или команду /remind, чтобы создать новое напоминание.",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


@start_router.message(F.text == "📝 Создать напоминание")
async def start_remind_flow(message: types.Message, state: FSMContext):
    """Кнопка в меню для запуска создания напоминания."""
    logger.info("User %s pressed 'Создать напоминание'", message.from_user.id)
    # Импортируем здесь, чтобы избежать циклических импортов на уровне модуля
    from bot.handlers.remind import remind

    await remind(message, state)


@start_router.message(F.text == "📋 Мои напоминания")
async def list_user_reminders(message: types.Message):
    """Кнопка в меню для проверки (просмотра) напоминаний."""
    user_id = int(message.from_user.id)
    logger.info("User %s requested reminders list", user_id)

    db = get_db()
    session = db.get_session()
    repo = ReminderRepository(session)

    reminders: list[Reminder] = await repo.get_user_reminders(user_id=user_id, limit=10)

    if not reminders:
        await message.answer(
            "Пока у тебя нет ни одного напоминания 🙈\n\n"
            "Нажми «📝 Создать напоминание», чтобы добавить первое!",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    lines: list[str] = []
    for rem in reminders:
        status = "⏳ в ожидании" if rem.status == "pending" else "✅ отправлено"
        remind_at = rem.remind_at.strftime("%d.%m.%Y %H:%M")
        lines.append(f"• [{status}] {remind_at} — {rem.text}")

    text = "Вот твои последние напоминания 📋:\n\n" + "\n".join(lines)
    await message.answer(text, reply_markup=MAIN_MENU_KEYBOARD)