import os
import logging
from multiprocessing import Process
from settings import get_settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def start_telegram_bot():
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
    from bot import GrotemServerConnector

    def start(update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Использование для чата {update.effective_chat.id}: <Название решения>, [сброс]"
        )

    def echo(update, context):
        sn = str(update.message.text).strip().split(' ')[0]
        bot_settings = get_settings()
        bot = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])

        if 'сброс' in str(update.message.text).lower():
            result = bot.reset_lic_count(solution_name=sn)
            if not result:
                response_text = f"Couldn't reset licences for solution {sn}: {bot.error_description}"
            else:
                response_text = f'Reset licences for solution {sn}: {bot.data}'
                result = bot.get_lic_info(solution_name=sn)
                if not result:
                    response_text += f"\r\nCouldn't check licences after update for solution {sn}: {bot.error_description}"
                else:
                    response_text += f" \r\nLicences after reset: {bot.data}"
        else:
            _ = bot.get_lic_info(solution_name=sn)
            response_text = f'{bot.data}'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
        if bot_settings['admin_chat'] != '' and bot_settings['admin_chat'] != str(update.effective_chat.id):
            context.bot.send_message(
                chat_id=bot_settings['admin_chat'],
                text=f"Chat {update.effective_chat.username} - {update.effective_chat.id}: {response_text}"
            )

    bot_settings = get_settings()
    bot = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])

    if not bot.check_connection():
        raise ConnectionError(f'Unable connect to Bitmobile server {bot_settings["bitmobile_host"]}')

    updater = Updater(token=bot_settings['telegram_bot_token'], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    updater.start_polling()
    updater.idle()


def start_web_api():
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    from bot import GrotemServerConnector

    settings = get_settings()
    connector = GrotemServerConnector(settings['bitmobile_host'], settings['root_password'])

    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.get("/")
    def index():
        return {"message": "Grotem Lic API is running"}

    @app.get("/solutions/{solution_name}/licenses")
    def get_licenses(solution_name: str):
        if not connector.get_lic_info(solution_name):
            return JSONResponse(status_code=400, content={"error": connector.error_description})
        return connector.data

    @app.post("/solutions/{solution_name}/reset")
    def reset_licenses(solution_name: str):
        if not connector.reset_lic_count(solution_name):
            return JSONResponse(status_code=400, content={"error": connector.error_description})
        return {"status": "ok"}

    @app.post("/solutions/{solution_name}/set/{count}")
    def set_licenses(solution_name: str, count: int):
        if not connector.set_lic_count(solution_name, lic_count=count):
            return JSONResponse(status_code=400, content={"error": connector.error_description})
        return {"status": "ok"}

    uvicorn.run(app, host="0.0.0.0", port=8000)


def main():
    mode = os.getenv("MODE", "both").lower()  # 'bot', 'web', or 'both'
    logger.info(f"Starting in MODE={mode}")

    if mode == "bot":
        start_telegram_bot()
    elif mode == "web":
        start_web_api()
    elif mode == "both":
        # Параллельный запуск
        Process(target=start_telegram_bot).start()
        Process(target=start_web_api).start()
    else:
        raise ValueError("Unknown MODE: use 'bot', 'web' or 'both'")


if __name__ == '__main__':
    main()
