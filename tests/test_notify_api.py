from fastapi.testclient import TestClient
from receive_notification_request import app


def test_notify_route(monkeypatch):
    called = {}

    async def fake_send(user_id, message):
        called["user_id"] = user_id
        called["message"] = message

    monkeypatch.setattr("receive_notification_request.send_notification", fake_send)

    client = TestClient(app)
    response = client.post("/notify/?user_id=123&message=Hi!")

    assert response.status_code == 200
    assert response.json() == {"status": "sent"}
    assert called["user_id"] == 123
    assert called["message"] == "Hi!"
