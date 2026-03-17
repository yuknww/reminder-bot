import asyncio
import json
import logging
from datetime import datetime
import aio_pika

from bot.config import config
from bot.database.db import get_db
from bot.database.repository import ReminderRepository

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 20

async def get_repository() -> ReminderRepository:
    db = get_db()
    async with db.get_session() as session:
        return ReminderRepository(session)

async def listener():
    logger.info("Starting reminders listener loop")

    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)

    async with connection:
        repository = await get_repository()
        channel = await connection.channel()
        await channel.declare_queue("reminders", durable=True)

        while True:
            try:
                reminders = await repository.get_overdue()
                logger.info("Found %d overdue reminders", len(reminders))

                for rem in reminders:
                    body = {
                        "user_id": rem.user_id,
                        "remind_id": rem.id,
                        "remind_text": rem.text,
                        "created_at": datetime.strftime(rem.remind_at, "%d.%m.%Y %H:%M"),
                    }

                    await channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(body).encode(),
                            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        ),
                        routing_key="reminders",
                    )
                    logger.info("Reminder %s queued for user %s", rem.id, rem.user_id)
            except Exception as e:
                logger.error("Error in reminders listener loop: %s", e)

            await asyncio.sleep(POLL_INTERVAL_SECONDS)