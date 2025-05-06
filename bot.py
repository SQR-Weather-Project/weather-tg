import asyncio
import os

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from watchfiles import awatch

from config import BACKEND_URL
from handlers import create_router
from models import NotificationSettings

router = create_router()
storage = MemoryStorage()

load_dotenv()

bot = Bot(token=os.getenv("TG_BOT_TOKEN"))

dp = Dispatcher(storage=storage)


@router.message(Command("start"))
async def start(msg: Message):
    command_parts = msg.text.split(maxsplit=1)

    if len(command_parts) == 2:
        token = command_parts[1]
        telegram_id = msg.from_user.id
        auth_token = os.getenv("TELEGRAM_SERVICE_HEADER_TOKEN")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{BACKEND_URL}/user/successful_login?authorization_token={auth_token}",
                    params={
                        "token": token,
                        "telegram_id": telegram_id,
                    },
                ) as resp:
                    if resp.status == 200:
                        await msg.answer(f"⚠️ Для завершения авторизации скопируй ссылку и открой её в браузере: \n\n{(await resp.json())['callback_url']}")

                    else:
                        await msg.answer(f"⚠️ Ошибка авторизации: {await resp.text()}")
            except Exception as e:
                await msg.answer(f"❌ Ошибка запроса: {str(e)}")
    else:
        await msg.answer(f"👋 Привет! Твой Telegram ID: {msg.from_user.id}")


@router.message(Command("settings"))
async def start_settings(msg: Message, state: FSMContext):
    await state.set_state(NotificationSettings.frequency)
    await msg.answer("Enter notification frequency (in minutes):")


@router.message(NotificationSettings.frequency)
async def set_frequency(msg: Message, state: FSMContext):
    try:
        frequency = int(msg.text)
        if frequency <= 0:
            raise ValueError
        await state.update_data(frequency=frequency)
    except ValueError:
        await msg.answer("⚠️ Please enter a valid positive number (minutes):")
        return

    await state.set_state(NotificationSettings.parameter)
    await msg.answer(
        "Please choose a parameter:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Pressure")],
                [KeyboardButton(text="Temperature")],
                [KeyboardButton(text="Humidity")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


@router.message(NotificationSettings.parameter)
async def set_parameter(msg: Message, state: FSMContext):
    await state.update_data(parameter=msg.text)
    await state.set_state(NotificationSettings.filter_type)
    await msg.answer(
        "Please choose a filter:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="above")], [KeyboardButton(text="below")]],
            resize_keyboard=True,
        ),
    )


@router.message(NotificationSettings.filter_type)
async def set_filter(msg: Message, state: FSMContext):
    await state.update_data(filter_type=msg.text)
    await state.set_state(NotificationSettings.threshold)
    await msg.answer(
        f"Notify if {(await state.get_data()).get('parameter')} "
        f"is {msg.text}... (enter threshold value)"
    )


@router.message(NotificationSettings.threshold)
async def set_threshold(msg: Message, state: FSMContext):
    await state.update_data(threshold=float(msg.text))
    await state.set_state(NotificationSettings.city)
    await msg.answer("Select a city (optional), or type 'skip':")


@router.message(NotificationSettings.city)
async def set_city(msg: Message, state: FSMContext):
    if msg.text.lower() != "skip":
        await state.update_data(city=msg.text)
    else:
        await state.update_data(city=None)

    # TODO: запустить воркер для отправления таких уведов

    data = await state.get_data()
    await msg.answer(
        f"✅ Settings saved:\n"
        f"• Frequency: {data['frequency']} min\n"
        f"• Parameter: {data['parameter']}\n"
        f"• Filter: {data['filter_type']} {data['threshold']}\n"
        f"• City: {data['city'] or 'Not specified'}"
    )


@router.message(Command("mysettings"))
async def get_user_settings(msg: Message, state: FSMContext):
    data = await state.get_data()
    if not data:
        await msg.answer(
            "⚠️ You don't have any saved " "settings yet. Use /settings to set them up."
        )
        return

    await msg.answer(
        f"🔔 Your notification settings:\n"
        f"• Frequency: {data.get('frequency')} min\n"
        f"• Parameter: {data.get('parameter')}\n"
        f"• Filter: {data.get('filter_type')} {data.get('threshold')}\n"
        f"• City: {data.get('city') or 'Not specified'}"
    )


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
