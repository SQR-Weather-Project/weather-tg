import pytest
from aioresponses import aioresponses
from unittest.mock import AsyncMock
from send_notification import fetch_and_send_weather


@pytest.mark.asyncio
async def test_fetch_and_send_weather_above_threshold(monkeypatch):
    mock_send_message = AsyncMock()

    monkeypatch.setattr("send_notification.bot.send_message",
                        mock_send_message)

    filters = type("Filters", (), {
        "param": "temperature",
        "type": "above",
        "value": 20,
        "city": "Kazan"
    })()

    weather_response = {
        "temperature": 25,
        "feels_like": 27,
        "pressure": 1010,
        "humidity": 40
    }

    with aioresponses() as mocked:
        url = (
            f"http://127.0.0.1:8000/weather?"
            f"city={filters.city}&user_token=fake_token"
        )

        mocked.get(url, payload=weather_response)

        await fetch_and_send_weather(telegram_id=123456,
                                     auth="fake_token", filters=filters)

        mock_send_message.assert_called_once()
        assert "Temperature: 25 °C" in mock_send_message.call_args[1]["text"]


@pytest.mark.asyncio
async def test_fetch_and_send_weather_below_threshold(monkeypatch):
    mock_send_message = AsyncMock()
    monkeypatch.setattr("send_notification.bot.send_message",
                        mock_send_message)

    filters = type("Filters", (), {
        "param": "humidity",
        "type": "below",
        "value": 50,
        "city": "Kazan"
    })()

    weather_response = {
        "temperature": 15,
        "feels_like": 13,
        "pressure": 1005,
        "humidity": 45
    }

    with aioresponses() as mocked:
        url = (
            f"http://127.0.0.1:8000/weather?"
            f"city={filters.city}&user_token=fake_token"
        )

        mocked.get(url, payload=weather_response)

        await fetch_and_send_weather(telegram_id=654321,
                                     auth="fake_token", filters=filters)

        mock_send_message.assert_called_once()
        assert "Humidity: 45%" in mock_send_message.call_args[1]["text"]


@pytest.mark.asyncio
async def test_fetch_and_send_weather_no_notification(monkeypatch):
    mock_send_message = AsyncMock()
    monkeypatch.setattr("send_notification.bot.send_message",
                        mock_send_message)

    filters = type("Filters", (), {
        "param": "pressure",
        "type": "above",
        "value": 1020,
        "city": "Kazan"
    })()

    weather_response = {
        "temperature": 18,
        "feels_like": 17,
        "pressure": 1010,
        "humidity": 60
    }

    with aioresponses() as mocked:
        url = (
            f"http://127.0.0.1:8000/weather?"
            f"city={filters.city}&user_token=fake_token"
        )

        mocked.get(url, payload=weather_response)

        await fetch_and_send_weather(telegram_id=999999,
                                     auth="fake_token", filters=filters)

        mock_send_message.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_and_send_weather_error_response(monkeypatch):
    mock_send_message = AsyncMock()
    monkeypatch.setattr("send_notification.bot.send_message",
                        mock_send_message)

    filters = type("Filters", (), {
        "param": "temperature",
        "type": "above",
        "value": 10,
        "city": "Kazan"
    })()

    with aioresponses() as mocked:

        url = (
            f"http://127.0.0.1:8000/weather?"
            f"city={filters.city}&user_token=fake_token"
        )

        mocked.get(url, status=500)

        await fetch_and_send_weather(
            telegram_id=123456, auth="fake_token", filters=filters)

        mock_send_message.assert_called_once()
        assert "Error to fetch "
        "weather" in mock_send_message.call_args[1]["text"]
