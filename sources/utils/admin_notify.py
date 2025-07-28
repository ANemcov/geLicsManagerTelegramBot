import httpx
from settings import get_settings

async def notify_admin_about_unauthorized(user_id: int, username: str, chat_id: int = None, source: str = "unknown"):
    settings = get_settings()
    token = settings["telegram_bot_token"]
    admin_chat = settings["admin_chat"]

    text = (
        f"🚨 Неавторизованный вызов из {source}:\n"
        f"👤 User ID: {user_id}\n"
        f"🔗 Username: @{username or 'нет'}\n"
        f"💬 Chat ID: {chat_id or 'N/A'}"
    )

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": admin_chat, "text": text}
        )
