# sources/utils/telegram_auth.py

import hashlib
import hmac
import urllib.parse
import json
from typing import Dict


def parse_init_data(init_data_str: str) -> Dict[str, str]:
    parsed = dict(urllib.parse.parse_qsl(init_data_str, keep_blank_values=True))
    return parsed


def is_valid_init_data(init_data: str, bot_token: str) -> bool:
    try:
        data = parse_init_data(init_data)
        hash_from_telegram = data.pop("hash")

        sorted_data = sorted((k, v) for k, v in data.items())
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_data)

        secret_key = hashlib.sha256(bot_token.encode()).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        return hmac.compare_digest(calculated_hash, hash_from_telegram)
    except Exception:
        return False


def get_user_from_init_data(init_data: str) -> dict:
    """Парсит JSON-поле user из initData (не проверяя подпись)"""
    data = parse_init_data(init_data)
    return json.loads(data['user'])
