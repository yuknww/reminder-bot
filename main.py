import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def main():
    global db
    db = init_db("sqlite+aiosqlite:///./reminders.db")
    dp.include_router(start_router)
    dp.include_router(remind_router)
    logger.info("Start bot")
    await db.create_tables()
    asyncio.create_task(listener(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())