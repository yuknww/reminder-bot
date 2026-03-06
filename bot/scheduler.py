import asyncio
import logging
from datetime import datetime

from bot.database.db import get_db
from bot.database.repository import ReminderRepository

logger = logging.getLogger(__name__)


async def listener(bot):
    print("Listening to reminders")
    db = get_db()
    session = db.get_session()
    remind = ReminderRepository(session)

    while True:
        reminds = await remind.get_overdue()
        logger.info(f"Обнаружено {len(reminds)} напоминаний")
        for rem in reminds:
            if rem.remind_at <= datetime.now():
                created_at = datetime.strftime(rem.remind_at, "%Y-%m-%d")
                text = (f"Ваше напоминание от {created_at}:\n\n"
                        f"{rem.text}")

                await bot.send_message(rem.user_id, text)
                await remind.mark_as_sent(rem.id)
                logger.info(f"Напоминание отправлено пользователю")
        await asyncio.sleep(20)