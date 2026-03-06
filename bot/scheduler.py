import asyncio
import logging
from datetime import datetime

from bot.database.db import get_db
from bot.database.repository import ReminderRepository

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 20


async def listener(bot):
    logger.info("Starting reminders listener loop")
    db = get_db()
    session = db.get_session()
    repository = ReminderRepository(session)

    while True:
        try:
            reminders = await repository.get_overdue()
            logger.info("Found %d overdue reminders", len(reminders))

            for rem in reminders:
                if rem.remind_at <= datetime.now():
                    created_at = datetime.strftime(rem.remind_at, "%d.%m.%Y %H:%M")
                    text = (
                        "🔔 Напоминание!\n\n"
                        f"Ты просил(а) напомнить {created_at}:\n"
                        f"{rem.text}\n\n"
                        "Хорошего дня 😊"
                    )

                    await bot.send_message(rem.user_id, text)
                    await repository.mark_as_sent(rem.id)
                    logger.info("Reminder %s sent to user %s", rem.id, rem.user_id)
        except Exception as e:
            logger.error("Error in reminders listener loop: %s", e)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)