from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import Reminder


class ReminderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, text: str, remind_at: datetime) -> Reminder:
        """ Создать напоминание """
        reminder = Reminder(
            user_id=user_id,
            text=text,
            remind_at=remind_at
        )
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)

        return reminder

    async def get_by_id(self, reminder_id: int) -> Reminder | None:
        """ Получить напоминание по id """
        result = await self.session.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        return result.scalar_one_or_none()


    async def get_overdue(self) -> list[Reminder]:
        """ Получить просроченные напоминания """
        now = datetime.now()
        result = await self.session.execute(
            select(Reminder).where(
                Reminder.status == "pending",
                Reminder.remind_at <= now
            )
        )
        return list(result.scalars().all())

    async def mark_as_sent(self, reminder_id: int) -> None:
        """ Пометить как отправленное """
        await self.session.execute(
            update(Reminder)
            .where(Reminder.id == reminder_id)
            .values(status="sent", sent_at=datetime.now())
        )
        await self.session.commit()

    async def get_user_reminders(self, user_id: int, limit: int = 10) -> list[Reminder]:
        """ Получить все напоминания пользователя """
        result = await self.session.execute(
            select(Reminder)
            .where(Reminder.user_id == user_id)
            .order_by(Reminder.created_at.desc())
            .limit(limit)
        )

        return list(result.scalars().all())
