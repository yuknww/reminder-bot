from sqlalchemy import Integer, String, DateTime, BigInteger, Column
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    text = Column(String, nullable=False)
    remind_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String, default='pending')
    sent_at = Column(DateTime, nullable=True)
