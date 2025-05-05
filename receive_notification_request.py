from fastapi import FastAPI
from send_notification import send_notification

app = FastAPI()

@app.post("/notify/")
async def notify_user(user_id: int, message: str):
    await send_notification(user_id, message)
    return {"status": "sent"}
