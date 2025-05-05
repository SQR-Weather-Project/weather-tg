import pytest

from send_notification import send_notification


@pytest.mark.asyncio
async def test_send_notification(monkeypatch):
    sent = {}

    class MockBot:
        async def send_message(self, chat_id, text):
            sent["chat_id"] = chat_id
            sent["text"] = text

    monkeypatch.setattr("send_notification.bot", MockBot())
    await send_notification(42, "Test")
    assert sent["chat_id"] == 42
    assert sent["text"] == "Test"
