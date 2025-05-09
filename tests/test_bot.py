from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, ReplyKeyboardMarkup, User

from bot import (get_user_settings, set_city, set_filter, set_frequency,
                 set_parameter, set_threshold, start, start_settings)
from models import NotificationSettings


def create_mock_message(text, user_id=123):
    message_mock = AsyncMock()

    message_mock.text = text
    message_mock.from_user = MagicMock(spec=User)
    message_mock.from_user.id = user_id
    message_mock.chat = MagicMock(spec=Chat)
    message_mock.chat.id = user_id
    message_mock.chat.type = "private"

    message_mock.answer = AsyncMock()

    return message_mock


@pytest.mark.asyncio
async def test_start_command():
    message_mock = create_mock_message("/start", user_id=123)
    await start(message_mock)
    message_mock.answer.assert_called_once_with(
        f"👋 Привет! Твой Telegram ID: {message_mock.from_user.id}")


@pytest.mark.asyncio
async def test_start_settings():
    message_mock = create_mock_message("/settings")
    state = AsyncMock()
    await start_settings(message_mock, state)
    state.set_state.assert_called_once_with(NotificationSettings.frequency)
    message_mock.answer.assert_called_once_with(
        "Enter notification frequency (in minutes):"
    )


@pytest.mark.asyncio
async def test_set_frequency_valid():
    message_mock = create_mock_message("10")
    state = AsyncMock()
    await set_frequency(message_mock, state)
    state.update_data.assert_called_once_with(frequency=10)
    state.set_state.assert_called_once_with(NotificationSettings.parameter)
    message_mock.answer.assert_called_once()
    call_args, call_kwargs = message_mock.answer.call_args
    reply_markup = call_kwargs.get("reply_markup")
    assert isinstance(reply_markup, ReplyKeyboardMarkup)
    assert [btn.text for row in reply_markup.keyboard for btn in row] == [
        "Pressure",
        "Temperature",
        "Humidity",
    ]


@pytest.mark.asyncio
async def test_set_frequency_invalid():
    message_mock = create_mock_message("abc")
    state = AsyncMock()
    await set_frequency(message_mock, state)
    state.update_data.assert_not_called()
    state.set_state.assert_not_called()
    message_mock.answer.assert_called_once_with(
        "⚠️ Please enter a valid positive number (minutes):"
    )


@pytest.mark.asyncio
async def test_set_parameter():
    message_mock = create_mock_message("Pressure")
    state = AsyncMock()
    await set_parameter(message_mock, state)
    state.update_data.assert_called_once_with(parameter="Pressure")
    state.set_state.assert_called_once_with(NotificationSettings.filter_type)
    message_mock.answer.assert_called_once()
    call_args, call_kwargs = message_mock.answer.call_args
    reply_markup = call_kwargs.get("reply_markup")
    assert isinstance(reply_markup, ReplyKeyboardMarkup)
    assert [btn.text for row in reply_markup.keyboard for btn in row] == [
        "above",
        "below",
    ]


@pytest.mark.asyncio
async def test_set_filter():
    message_mock = create_mock_message("above")
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"parameter": "Temperature"})
    await set_filter(message_mock, state)
    state.get_data.assert_called_once()
    state.update_data.assert_called_once_with(filter_type="above")
    state.set_state.assert_called_once_with(NotificationSettings.threshold)
    message_mock.answer.assert_called_once_with(
        "Notify if Temperature is above... (enter threshold value)"
    )


@pytest.mark.asyncio
async def test_set_threshold():
    message_mock = create_mock_message("25.5")
    state = AsyncMock()
    await set_threshold(message_mock, state)
    state.update_data.assert_called_once_with(threshold=25.5)
    state.set_state.assert_called_once_with(NotificationSettings.city)
    message_mock.answer.assert_called_once_with(
        "Select a city"
    )


@pytest.mark.asyncio
async def test_set_city_with_city():
    message_mock = create_mock_message("Moscow")
    state = AsyncMock()

    initial_state_data = {
        "frequency": 10,
        "parameter": "Humidity",
        "filter_type": "below",
        "threshold": 30.0,
    }

    final_state_data = initial_state_data.copy()
    final_state_data["city"] = "Moscow"
    state.get_data = AsyncMock(return_value=final_state_data)

    await set_city(message_mock, state)

    state.update_data.assert_called_once_with(city="Moscow")
    state.get_data.assert_called_once()

    expected_answer = (
        "✅ Settings saved:\n"
        f"• Notifications will be send every "
        f"{final_state_data['frequency']} min\n"
        f"• Parameter: {final_state_data['parameter']}\n"
        f"• Filter: {final_state_data['filter_type']} "
        f"{final_state_data['threshold']}\n"
        f"• City: Moscow"
    )
    message_mock.answer.assert_called_once_with(expected_answer)


@pytest.mark.asyncio
async def test_get_user_settings_with_data():
    message_mock = create_mock_message("/mysettings")
    state = AsyncMock()
    state_data = {
        "frequency": 30,
        "parameter": "Temperature",
        "filter_type": "above",
        "threshold": 25.5,
        "city": "London",
    }
    state.get_data = AsyncMock(return_value=state_data)
    await get_user_settings(message_mock, state)
    state.get_data.assert_called_once()
    expected_answer = (
        "🔔 Your notification settings:\n"
        f"• Frequency: {state_data['frequency']} min\n"
        f"• Parameter: {state_data['parameter']}\n"
        f"• Filter: {state_data['filter_type']} {state_data['threshold']}\n"
        f"• City: London"
    )
    message_mock.answer.assert_called_once_with(expected_answer)


@pytest.mark.asyncio
async def test_get_user_settings_no_data():
    message_mock = create_mock_message("/mysettings")
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    await get_user_settings(message_mock, state)
    state.get_data.assert_called_once()
    message_mock.answer.assert_called_once_with(
        "⚠️ You don't have any saved settings yet. " "Use "
        "/settings to set them up."
    )
