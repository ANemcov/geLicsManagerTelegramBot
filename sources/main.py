import os
import logging
from multiprocessing import Process
import sys
from settings import get_settings


logging.basicConfig(
    level=logging.INFO, 
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,  # лог в stdout (подходит для Docker/CI)
    force=True  # важно, если кто-то уже инициализировал logging раньше
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def start_telegram_bot():
    from telegram.ext import CommandHandler, MessageHandler
    from telegram.ext import filters
    from telegram.ext import ApplicationBuilder
    from bot import GrotemServerConnector

    async def start(update, context):
        bot_settings = get_settings()
        
        user_id = update.effective_user.id
        
        if user_id not in bot_settings["allowed_users"]:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Доступ запрещён")
            return
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Использование для чата {update.effective_chat.id}: <Название решения>, [сброс]"
        )

    async def echo(update, context):
        
        bot_settings = get_settings()
        
        if update.effective_user.id not in bot_settings["allowed_users"]:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Доступ запрещён")
            return
        
        if update.message and update.message.text:
            sn = str(update.message.text).strip().split(' ')[0]
        else:
            # обработать другие случаи или пропустить
            return
        
        bot = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])

        if 'сброс' in str(update.message.text).lower():
            result = bot.reset_lic_count(solution_name=sn)
            if not result:
                response_text = f"Couldn't reset licenses for solution {sn}: {bot.error_description}"
            else:
                response_text = f'Reset licenses for solution {sn}: {bot.data}'
                result = bot.get_lic_info(solution_name=sn)
                if not result:
                    response_text += f"\r\nCouldn't check licenses after update for solution {sn}: {bot.error_description}"
                else:
                    response_text += f" \r\nLicenses after reset: {bot.data}"
        else:
            _ = bot.get_lic_info(solution_name=sn)
            response_text = f'{bot.data}'

        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
        if bot_settings['admin_chat'] != '' and bot_settings['admin_chat'] != str(update.effective_chat.id):
            await context.bot.send_message(
                chat_id=bot_settings['admin_chat'],
                text=f"Chat {update.effective_chat.username} - {update.effective_chat.id}: {response_text}"
            )

    bot_settings = get_settings()
    bot = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])

    if not bot.check_connection():
        raise ConnectionError(f'Unable connect to Bitmobile server {bot_settings["bitmobile_host"]}')

    app = ApplicationBuilder().token(bot_settings['telegram_bot_token']).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    app.run_polling()


def main():
    mode = os.getenv("MODE", "both").lower()  # 'bot', 'web', or 'both'
    logger.info(f"Starting in MODE={mode}")

    if mode == "bot":
        start_telegram_bot()
    elif mode == "web":
        import uvicorn
        uvicorn.run("web_api:app", host="0.0.0.0", port=8000)
    elif mode == "both":
        Process(target=start_telegram_bot).start()
        Process(target=lambda: __import__('uvicorn').run("web_api:app", host="0.0.0.0", port=8000)).start()
    else:
        raise ValueError("Unknown MODE: use 'bot', 'web' or 'both'")


if __name__ == '__main__':
    main()
