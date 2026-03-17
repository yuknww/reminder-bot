import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

config = Config()
