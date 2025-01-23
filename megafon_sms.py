# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
from dotenv import load_dotenv


def megafon_send_sms(phone: str, message: str = ''):
    url = 'https://hub.megafon.ru/messaging/v1/send'
    extDataDir = os.getcwd()
    if getattr(sys, 'frozen', False):
        extDataDir = sys._MEIPASS
    load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

    token = os.getenv("MEGAFON_SMS_TOKEN")
    sms_text = "Добрый день. " \
               "{0}." \
               " С уважением, поддержка X5 Transport"

    pwd_rst_msg = 'В приложении X5Transport Вам был установлен временный пароль, равный 6 последним цифрам вашего номера телефона. Сброс пароля осуществляется по кнопке "Забыли пароль" в окне ввода логина-пароля'

    if message == '':
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