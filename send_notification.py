import os

from aiogram import Bot
from dotenv import load_dotenv
import aiohttp

load_dotenv()

bot = Bot(token=os.getenv("TG_BOT_TOKEN"))


async def fetch_and_send_weather(telegram_id, auth, filters):
    async with aiohttp.ClientSession() as session:
        url = (
            f"http://127.0.0.1:8000/weather?"
            f"city={filters.city}&user_token={auth}"
        )
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                condition = (
                    data[filters.param] > filters.value
                    if filters.type == "above"
                    else data[filters.param] < filters.value
                )
                if condition:
                    text = (
                        "Weather:\n"
                        f"Temperature: {data['temperature']} °C\n"
                        f"Feels like: {data['feels_like']} °C\n"
                        f"Pressure: {data['pressure']} hPa\n"
                        f"Humidity: {data['humidity']}%\n"
                    )
                    await bot.send_message(chat_id=telegram_id, text=text)
            else:
                await bot.send_message(
                    chat_id=telegram_id,
                    text="Error to fetch weather"
                )
