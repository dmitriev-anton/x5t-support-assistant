# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import logging


def megafon_send_sms(phone: str, message: str = '', password: str = ''):
    url = 'https://hub.megafon.ru/messaging/v1/send'

    # # Настройка логирования
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(levelname)s - %(message)s',
    #     filename='app_debug.log',
    #     filemode='w'
    # )
    #
    # def resource_path(relative_path):
    #     """Возвращает корректный путь для ресурсов в режиме PyInstaller"""
    #     if hasattr(sys, '_MEIPASS'):
    #         return os.path.join(sys._MEIPASS, relative_path)
    #     return os.path.join(os.path.abspath("."), relative_path)
    #
    # # Основная директория
    # if getattr(sys, 'frozen', False):
    #     base_dir = os.path.dirname(sys.executable)
    # else:
    #     base_dir = os.path.dirname(os.path.abspath(__file__))
    #
    # # Пути к конфигурационным файлам
    # env_path = resource_path('.env')  # Для .env во временной директории
    # config_path = os.path.join(base_dir, 'config.cfg')  # Для config.cfg рядом с EXE
    #
    # logging.info(f"Base directory: {base_dir}")
    # logging.info(f".env path: {env_path}")
    # logging.info(f"config.cfg path: {config_path}")
    #
    # # Загрузка .env из ресурсов
    # if os.path.exists(env_path):
    #     dotenv.load_dotenv(dotenv_path=env_path, override=True)
    #     logging.info(".env loaded from resources")
    # else:
    #     logging.warning(".env not found in resources")
    #
    # # Загрузка config.cfg
    # if os.path.exists(config_path):
    #     dotenv.load_dotenv(dotenv_path=config_path, override=True)
    #     logging.info("config.cfg loaded")
    # else:
    #     logging.error(f"config.cfg not found at {config_path}")
    #
    # # Проверка переменных (добавьте свои)
    # required_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    # for var in required_vars:
    #     value = os.getenv(var)
    #     if value is None:
    #         logging.error(f"Missing variable: {var}")
    #     else:
    #         logging.info(f"{var} = {value if var != 'DB_PASSWORD' else '***'}")

    token = os.getenv("MEGAFON_SMS_TOKEN")

    sms_text = "Добрый день. " \
               "{0}." \
               " С уважением, поддержка X5 Transport"

    pwd_rst_msg = f'В приложении X5Transport Вам был установлен пароль, равный {password} . Сброс пароля осуществляется по кнопке "Забыли пароль" в окне ввода логина-пароля'

    if (message == '') and password:
        message = pwd_rst_msg

    headers = {
        'Content-Type': 'application/json',
        'Authorization' : f'Basic {token}'
    }

    body = {
        'scenario': [
            {
                "channel": "sms",
                "recipient": {
                    "type": "MSISDN",
                    "value": int(f'7{phone}')
                },
                "sender": "HotlineX5",
                "text": sms_text.format(message)
            }
        ]
    }


    try:
        response = requests.post(url=url, headers=headers, data=json.dumps(body), verify=False)
        return response.json(), body
    except Exception as error:
        return error


# print(megafon_send_sms('9127609251', 'тест'))