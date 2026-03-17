import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from bot.config import config
from bot.database.db import get_db
from bot.database.repository import ReminderRepository

logger = logging.getLogger(__name__)

async def get_repository() -> ReminderRepository:
    db = get_db()
    async with db.get_session() as session:
        return ReminderRepository(session)

async def on_message(message: AbstractIncomingMessage, bot) -> None:
    async with message.process():
        try:
            repo = await get_repository()
            data = json.loads(message.body)

            user_id = int(data['user_id'])
            remind_id = data['remind_id']
            remind_text = data['remind_text']
            created_at = data['created_at']

            text = (
                "🔔 Напоминание!\n\n"
                f"Ты просил(а) напомнить {created_at}:\n"
                f"{remind_text}\n\n"
                "Хорошего дня 😊"
            )
            await bot.send_message(user_id, text)
            await repo.mark_as_sent(remind_id)
            logger.info("Reminder %s sent to user %s", remind_id, user_id)
        except Exception as e:
            logger.error("Failed to send reminder: %s", e)
            raise

async def start_consumer(bot) -> None:
    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue("reminders", durable=True)

        await queue.consume(lambda msg: on_message(msg, bot))

        logger.info("Consumer started, waiting for reminders...")
        await asyncio.Future()