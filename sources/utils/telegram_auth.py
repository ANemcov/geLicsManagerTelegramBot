# sources/utils/telegram_auth.py

import hashlib
import hmac
import urllib.parse
import json
import logging
from typing import Dict
from urllib.parse import unquote
from fastapi import HTTPException, Header

from utils.admin_notify import notify_admin_about_unauthorized
from settings import get_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def parse_init_data(init_data_str: str) -> Dict[str, str]:
    parsed = dict(urllib.parse.parse_qsl(init_data_str, keep_blank_values=True))
    return parsed

def is_valid_init_data(init_data: str, bot_token: str) -> bool:
    try:
        prepared_init_data = unquote(init_data)
        # Разбиваем вручную, не декодируя значения
        pairs = [pair for pair in prepared_init_data.split('&') if not pair.startswith('hash=')]
        pairs.sort()  # сортировка по ключу
        data_check_string = '\n'.join(pairs)

        # HMAC_SHA256(bot_token, key="WebAppData")
        secret_key = hmac.new(
            "WebAppData".encode(), bot_token.encode(), hashlib.sha256
        ).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # Извлекаем оригинальный hash без декодирования
        received_hash = None
        for pair in prepared_init_data.split('&'):
            if pair.startswith("hash="):
                received_hash = pair[len("hash="):]
                break
        if received_hash is None:
            return False
        
        logger.debug(f'data_check_string: {data_check_string}', )
        logger.debug(f'calculated_hash: {calculated_hash}')
        logger.debug(f'received_hash: {received_hash}')

        return hmac.compare_digest(calculated_hash, received_hash)

    except Exception as e:
        logger.error(f'Validation error: {e}')
        return False


def get_user_from_init_data(init_data: str) -> dict:
    """Парсит JSON-поле user из initData (не проверяя подпись)"""
    data = parse_init_data(init_data)
    return json.loads(data['user'])


async def check_user_allowed(x_telegram_initdata: str, source: str = "WebApp"):
    settings = get_settings()
    user = get_user_from_init_data(x_telegram_initdata)
    user_id = int(user.get("id"))
    username = user.get("username", "")

    if user_id not in settings["allowed_users"]:
        await notify_admin_about_unauthorized(user_id, username, chat_id=None, source=source)
        raise HTTPException(status_code=403, detail="User not allowed")
    return user
