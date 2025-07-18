# -*- coding: utf-8 -*-
import requests
import json
from x5t_connect import db_request
# from x5t_connect_1line import db_request
import os
import sys
import dotenv
import random
import string
import secrets
import logging
from pathlib import Path


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

reg_api = os.getenv("DRIVER_REG_API")
info_api = os.getenv("DRIVER_INFO_API")
app_fleet  = os.getenv("APP_FLEET")
latest_user_agent = os.getenv("APP_VERSION")



def api_pwd_recovery_request(phone: str):
    # Получаем ид сессии
    api = f'http://{app_fleet}/info/v1/driver/password/recovery'

    headers = {
        'Content-Type': 'application/json',
        'Content-Length': '68',
        'Host': app_fleet,
        'User-Agent': latest_user_agent,
    }
    body = {
        'data': {'phone': phone},
    }

    try:
        response = requests.post(api, headers=headers, data=json.dumps(body), timeout=30, verify=False)
        # print(response)
        return response.json()['data']['verificationSessionId']
    except requests.exceptions.SSLError:
        return None


def pwd_code(verification_id: str):
    # Забираем код смс
    _ = ('SELECT code FROM \"core-verification-schema\".phone_verification_session '
         'where status = \'ACTIVE\' and id = \'{0}\'')
    temp = None
    temp = db_request(_.format(verification_id))
    # print(temp)
    return temp[0]['code']


def api_pwd_verify(code, phone, verification_id: str):
    # Подтверждаем смс в ГПН
    api = f'http://{app_fleet}/info/v1/driver/sms/verify'
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': '129',
        'Host': app_fleet,
        'User-Agent': latest_user_agent,
    }
    body = {
        'data': {
            'code': code,
            'phone': phone,
            'verificationSessionId': verification_id
        },
        'params': 'null'
    }

    try:
        response = requests.post(api, headers=headers, data=json.dumps(body), timeout=30, verify=False)
        # print(response.json())
        return response.json()['data']['result']
    except requests.exceptions.SSLError:
        return None


def api_pwd_create(phone, password, verification_id: str):
    api = f'http://{app_fleet}/info/v1/driver/password/create'
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': '122',
        'Host': app_fleet,
        'User-Agent': latest_user_agent,
    }
    body = {
        'data': {
            # 'phone' : phone,
            'password': password,
            'verificationSessionId': verification_id
        },
    }
    try:
        response = requests.post(api, headers=headers, data=json.dumps(body), timeout=30, verify=False)
        # print(response.json())
        return response.json()

    except requests.exceptions.SSLError:
        return None


def driver_pwd_reset(phone: str, password: str) -> object:
    """Сброс пароля"""
    verification_id = api_pwd_recovery_request(phone)
    if verification_id:
        pass_code = pwd_code(verification_id)
        if api_pwd_verify(pass_code, phone, verification_id):
            result = api_pwd_create(phone=phone, password=password, verification_id=verification_id)
            if result:

                return True
            else:
                return 'Отказ на шаге 3'
        else:
            return 'Отказ на шаге 2'
    else:
        return 'Отказ на шаге 1'


def api_driver_token(phone: str, password : str) -> str:
    """Получает токен из БД или выдает ошибку"""

    api = f'https://{info_api}/v1/auth/drivers/token'
    headers = {
        'Content-Type': 'application/json',
        # 'Cookie': '17b4e09f4ad0242ff0dcd2969ae02791=5dc45d0378d1e3bd72bbffecd742833e',
        'User-Agent': latest_user_agent,
        #'Host': info_api,
    }
    body = {
        'password': password,
        'userName': phone
    }

    try:
        response = requests.post(api, headers=headers, data=json.dumps(body), verify=False).json()
        if response['data'] == None:
            raise RuntimeError(response['error']['message'])
        else:
            return response['data']['accessToken']

    except requests.exceptions.SSLError:
        raise ConnectionError('Ошибка связи.')


def generate_password(length=8):
    if length < 4:
        raise ValueError("Длина пароля должна быть не менее 4 символов")

    # Наборы символов
    lowercase = "abcdefghjkmnpqrstuvwxyz"  # исключены l, i
    uppercase = "ABCDEFGHJKMNPQRSTUVWXYZ"  # исключены I, L, O
    digits = "23456789"  # исключены 0, 1
    punctuation = "[]?@{}"  # знаки препинания
    all_chars = lowercase + uppercase + digits

    # Гарантируем обязательные символы
    password = [
        secrets.choice(uppercase),  # одна заглавная
        secrets.choice(lowercase),  # одна строчная
        secrets.choice(digits),  # одна цифра
        secrets.choice(punctuation), # один знак препинания
        secrets.choice(digits), # одна цифра
        # secrets.choice(punctuation), # один знак препинания
    ]

    # Заполняем оставшуюся длину случайными символами
    remaining = length - 5
    if remaining > 0:
        password += [secrets.choice(all_chars) for _ in range(remaining)]

    # Перемешиваем для случайного порядка
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

# password = generate_password()
# print(password)
# print(api_driver_token('9601032336', 'c_LWs25B'))

# print(api_driver_token(''))
# print(driver_pwd_reset('9528643099', password))