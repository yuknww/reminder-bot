from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from bot.database.models import Base

class Database:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(
            db_url,
            echo=False,
        )

        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self):
        """ Создаёт все таблицы """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    def get_session(self) -> AsyncSession:
        return self.session_maker()

db: Database | None = None


def init_db(db_url: str) -> Database:
    """Инициализация БД"""
    global db
    db = Database(db_url)
    return db


def get_db() -> Database:
    """Получить экземпляр БД"""
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db