import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN, DATABASE_URL
from bot.database.db import init_db, Database
from bot.handlers.remind import remind_router
from bot.handlers.start import start_router
from bot.scheduler import listener

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db: Database | None = None

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

async def main():
    global db
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Check your .env configuration.")
        raise RuntimeError("BOT_TOKEN is not set")

    db_url = DATABASE_URL or "sqlite+aiosqlite:///./reminders.db"
    logger.info(f"Initializing database with url: {db_url}")

    db = init_db(db_url)
    dp.include_router(start_router)
    dp.include_router(remind_router)

    logger.info("Creating database tables (if not exist)")
    await db.create_tables()
    logger.info("Starting reminder listener")
    asyncio.create_task(listener(bot))
    logger.info("Starting bot polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())