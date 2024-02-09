# from os import read
import sqlite3
import configparser
import os
# from cryptography.fernet import Fernet

con = None
is_new_key = False


# def get_encryption_key():
#     key_file = open("key.txt", "a+")
#     key_file.seek(0)
#     key = key_file.readline().strip()
#     if not key:
#         key = Fernet.generate_key()
#         key_file.flush()
#         key_file.write(key.decode())
#         is_new_key = True
#     return key


def get_db_connection():
    conn = sqlite3.connect('settings.db')
    return conn


def close_db_connection(conn, commit=True):
    conn.close()


# def request_setting():
#     telegram_bot_token = input("telegram_bot_token: ")
#     utils_path = input("Utils file path: ").strip()
#     root_password = input("Root password: ").strip()
#     bitmobile_host = input("Bitmobile Host address: ").strip()
#     fern = Fernet(get_encryption_key())
#     root_password = fern.encrypt(root_password.encode())
#     return {'telegram_bot_token': telegram_bot_token,
#             'utils_path': utils_path,
#             'root_password': root_password,
#             'bitmobile_host': bitmobile_host}


# def init_settings(rewrite=False):
#     fern = Fernet(get_encryption_key())
#     rewrite = is_new_key
#     is_set = False
#     conn = get_db_connection()
#     cur = conn.cursor()
#     settings = None
#
#     cur.execute('''CREATE TABLE IF NOT EXISTS Settings
#                     (telegramBotToken text,
#                     UtilsPath text,
#                     rootPassword text,
#                     bitmobileHost)''')
#     for values in cur.execute('SELECT * FROM Settings LIMIT 1'):
#         is_set = True
#         settings = {'telegram_bot_token': values[0],
#                     'utils_path': values[1],
#                     'root_password': fern.decrypt(values[2]).decode(),
#                     'bitmobile_host': values[3]}
#
#     if rewrite:
#         is_set = False
#
#     if not is_set:
#         settings = request_setting()
#         cur.execute('''INSERT INTO Settings
#                         VALUES
#                         (:telegramBotToken, :UtilsPath, :rootPassword, :bitmobileHost)''', settings)
#         settings['rootPassword'] = fern.decrypt(settings['rootPassword']).decode()
#     conn.commit()
#     close_db_connection(conn)
#     return settings
#

def test_module():
    # conn = ConnDB()
    # cur = conn.cursor()
    # cur.execute('''DROP TABLE Settings''')
    # conn.commit()
    # Disconnect(conn)
    # init_settings(True)
    # print(getEncryptionKey())
    pass


def _load_settings_file():
    f_settings = {}
    working_directory = os.getcwd()
    config_filename = os.path.join(working_directory, 'config.ini')
    if os.path.exists(config_filename):
        config = configparser.ConfigParser()
        config.sections()
        config.read(config_filename)
        f_settings.update(config['TELEGRAM_BOT'])
    return f_settings


def _load_env_settings():
    env_settings = {}
    for env_item in [i for i in os.environ if i.startswith('TELEGRAM_BOT')]:
        param_name = env_item.split('__')[1].lower().strip()
        env_settings.update({param_name: os.environ[env_item]})
    return env_settings


def get_settings():
    settings = {'telegram_bot_token': '',
                'utils_path': '',
                'root_password': '',
                'bitmobile_host': '',
                'admin_chat': ''}

    settings.update(_load_settings_file())
    settings.update(_load_env_settings())

    return settings


if __name__ == '__main__':
    test_module()
