# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
from dotenv import load_dotenv


def megafon_send_sms(phone: str, message: str = '', password: str = ''):
    url = 'https://hub.megafon.ru/messaging/v1/send'
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)  # Директория с EXE
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Директория с исходным кодом

    # Загружаем .env (если он встроен или рядом)
    load_dotenv(os.path.join(base_dir, '.env'))  # Встроенный или внешний .env

    # Загружаем config.cfg из директории с EXE
    config_path = os.path.join(base_dir, 'config.cfg')

    if os.path.exists(config_path):
        load_dotenv(dotenv_path=config_path)  # Используем dotenv для загрузки .cfg
    else:
        raise FileNotFoundError(f"Config file not found: {config_path}")

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