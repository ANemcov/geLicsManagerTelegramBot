import logging
from flask import Flask, request, jsonify
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bot import GrotemServerConnector
from settings import get_settings
import urllib.parse, hashlib, hmac
import threading

# Настройка логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Flask-приложение для WebApp API
app = Flask(__name__)
bot_settings = get_settings()

# Telegram Bot start-команда
def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Использование для чата {update.effective_chat.id}: <Название решения>, [сброс]"
    )

# Telegram Bot текстовое сообщение
def echo(update, context):
    sn = str(update.message.text).strip().split(' ')[0]
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
                response_text += f" \r\licenses after reset: {bot.data}"
    else:
        _ = bot.get_lic_info(solution_name=sn)
        response_text = f'{bot.data}'

    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
    if bot_settings['admin_chat'] != '' and bot_settings['admin_chat'] != str(update.effective_chat.id):
        context.bot.send_message(
            chat_id=bot_settings['admin_chat'],
            text=f"Chat {update.effective_chat.username} - {update.effective_chat.id}: {response_text}"
        )

# Верификация WebApp от Telegram
def verify_telegram_webapp(data: str, hash_to_check: str) -> bool:
    secret = hashlib.sha256(bot_settings['telegram_bot_token'].encode()).digest()
    return hmac.compare_digest(
        hmac.new(secret, data.encode(), hashlib.sha256).hexdigest(),
        hash_to_check
    )

def validate_user(req):
    init_data = req.json.get('initData', '')
    init_data_dict = dict(urllib.parse.parse_qsl(init_data))
    hash_to_check = init_data_dict.pop('hash', '')
    check_string = '\n'.join(f'{k}={v}' for k, v in sorted(init_data_dict.items()))
    return verify_telegram_webapp(check_string, hash_to_check)

# Web API endpoints
@app.route('/api/solutions', methods=['POST'])
def get_solutions():
    if not validate_user(request): return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(["solution1", "solution2", "solution3"])

@app.route('/api/lic_info', methods=['POST'])
def get_lic_info():
    if not validate_user(request): return jsonify({'error': 'Unauthorized'}), 403
    sol = request.json.get('solution_name')
    connector = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])
    if not connector.check_connection(): return jsonify({'error': 'Server not available'}), 500
    if not connector.get_lic_info(sol): return jsonify({'error': connector.error_description}), 400
    return jsonify(connector.data)

@app.route('/api/reset_lic', methods=['POST'])
def reset_lic():
    if not validate_user(request): return jsonify({'error': 'Unauthorized'}), 403
    sol = request.json.get('solution_name')
    connector = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])
    if not connector.check_connection(): return jsonify({'error': 'Server not available'}), 500
    if not connector.reset_lic_count(sol): return jsonify({'error': connector.error_description}), 400
    return jsonify({'result': 'ok'})

@app.route('/api/set_lic', methods=['POST'])
def set_lic():
    if not validate_user(request): return jsonify({'error': 'Unauthorized'}), 403
    sol = request.json.get('solution_name')
    count = int(request.json.get('lic_count', 0))
    connector = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])
    if not connector.check_connection(): return jsonify({'error': 'Server not available'}), 500
    if not connector.set_lic_count(sol, count): return jsonify({'error': connector.error_description}), 400
    return jsonify({'result': 'ok'})

# Основной запуск

def run_bot():
    updater = Updater(token=bot_settings['telegram_bot_token'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    updater.start_polling()


def main():
    bot = GrotemServerConnector(bot_settings['bitmobile_host'], bot_settings['root_password'])
    if not bot.check_connection():
        raise ConnectionError(f'Unable connect to Bitmobile server {bot_settings["bitmobile_host"]}')

    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
