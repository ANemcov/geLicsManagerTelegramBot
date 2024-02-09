import logging
from bot import GrotemServerConnector
from settings import get_settings
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Использование для чата {update.effective_chat.id}: <Название решения>, [сброс]"
    )


def echo(update, context):
    # is_set_lic = str(update.message.text).strip().lower().find("сброс") >= 0
    sn = str(update.message.text).strip().split(' ')[0]
    bot_settings = get_settings()
    bot = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])
    if 'сброс' in str(update.message.text).lower():
        # result = bot.slic(sn)
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


def main():
    # settings = init_settings()
    # bot.settings = settings
    # bot.init()
    bot_settings = get_settings()
    bot = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])
    if not bot.check_connection():
        raise ConnectionError(f'Unable connect to Bitmobile server {bot_settings["bitmobile_host"]}')
    updater = Updater(token=bot_settings['telegram_bot_token'], use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
