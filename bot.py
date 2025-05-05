from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TG_BOT_TOKEN"))
dp = Dispatcher()


@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer(f"User ID: {msg.from_user.id}")
    # TODO: добавить простую авторизацию, чтобы на фронте понимать, что за уведы


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
