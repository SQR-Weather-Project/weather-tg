from aiogram import Bot
import os
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=os.getenv("TG_BOT_TOKEN"))

async def send_notification(user_id: int, text: str):
    await bot.send_message(chat_id=user_id, text=text)
