# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path
import dotenv
import requests
import json
from x5t_connect import db_request
from driver_api import api_driver_token
from tabulate import tabulate
from pandas import DataFrame
import logging

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

gpn_login = os.getenv("GPN_LOGIN")
gpn_pwd = os.getenv("GPN_PWD")
gpn_url = os.getenv("GPN_URL")
gpn_key = os.getenv("GPN_API_KEY")
barcode_api = os.getenv("BARCODE_API")

def gpn_auth():

    """Авторизация ГПН"""

    url = f"https://{gpn_url}/vip/v1/authUser/?login={gpn_login}&password={gpn_pwd}"

    headers = {
        'Content-Type': 'application/json',
        'Host': gpn_url,
        'api-key': gpn_key
        }

    body = {}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
        # print(result)
    except requests.exceptions.SSLError:
        return None


def get_vtk_info(card_num:str):
    _sql = (f'SELECT  azs_contract_id,  card_num,  '
           f'vtk_create_time, error_msg, azs_company_id, card_id, pin, confirm_mpc, tech_driver_id, card_status FROM '
           f'\"core-azs\".vtk_request where card_num = \'{card_num}\'')

    _sql2  = (f'SELECT cast(fc.number as text) as card_num, fc.code, fc.azs_company_id, fc.vtk ,vr.azs_contract_id,  vr.error_msg, '
              f'vr.azs_company_id, vr.card_id, vr.pin, vr.tech_driver_id, vr.card_status, td."name" '
              f'FROM "core-azs".fuel_cards fc 	'
              f'left join "core-azs".vtk_request vr on cast(fc.number as text) = vr.card_num 	'
              f'left join "core-azs".tech_driver td on vr.tech_driver_id = td.tech_driver_id  '
              f'where fc.number = \'{card_num}\'')

    resolve = db_request(_sql2)
    if resolve:
        return resolve[0]
    else:
        raise RuntimeError('Карта не обнаружена.')

def gpn_delete_mpc(card_num:str, session_id:str):

    """удаление МПК ГПН"""

    vtk = get_vtk_info(card_num)

    if vtk['azs_company_id'] != 1002: raise RuntimeError('Карта не ГПН.')

    url = "https://{0}/vip/v2/cards/{1}/deleteMPC".format(gpn_url, vtk['card_id'])

    headers = {
        'contract_id': vtk['azs_contract_id'],
        'Content-Type': 'application/json',
        'Host': gpn_url,
        'api_key': gpn_key,
        'session_id': session_id
        }

    body = {}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None

def gpn_init_mpc(card_num: str, sess_id: str):
    """Выпуск мпк"""


    vtk = get_vtk_info(card_num)

    if vtk['azs_company_id'] != 1002: raise RuntimeError('Карта не ГПН.')

    url = "https://{0}/vip/v2/cards/{1}/initMPC".format(gpn_url, vtk['card_id'])

    headers = {
        'contract_id': vtk['azs_contract_id'],
        'Content-Type': 'application/json',
        'Host': gpn_url,
        'api_key': gpn_key,
        'session_id': sess_id,
        'Cookie' : 'session-cookie=1758d005c3ff7477256ce8c118991a243e122dbe22a11716d5852fa58e676592a5af860934b4f64885ea6dc80d50e2ed'
        }

    body = {
        'user_id': vtk['tech_driver_id'],
        'pin': vtk['pin'],
        'device_id': 'xxxx',
        'device_name': 'Android1111'
        }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None


def gpn_confirm_mpc(card_num: str, economist_code:str, session_id: str):
    """подтверждение МПК ГПН"""


    vtk = get_vtk_info(card_num)

    if vtk['azs_company_id'] != 1002: raise RuntimeError('Карта не ГПН.')

    url = "https://{0}/vip/v2/cards/{1}/confirmMPC".format(gpn_url, vtk['card_id'])
    headers = {
        'Content-Type': 'application/json',
        'contract_id': vtk['azs_contract_id'],
        'Host': gpn_url,
        'api-key': gpn_key,
        'session_id': session_id,
        'Cookie': 'session-cookie=1758d005c3ff7477256ce8c118991a243e122dbe22a11716d5852fa58e676592a5af860934b4f64885ea6dc80d50e2ed'
        }

    body = {
        'code': economist_code
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None


def gpn_reset_mpc(card_num: str, session_id: str):
    """сброс мпк"""


    vtk = get_vtk_info(card_num)

    if vtk['azs_company_id'] != 1002: raise RuntimeError('Карта не ГПН.')

    url = "https://{0}/vip/v2/cards/{1}/resetMPC?type = ResetCounterMPC".format(gpn_url, vtk['card_id'])

    headers = {
        'contract_id': vtk['azs_contract_id'],
        'Content-Type': 'application/json',
        'Host': gpn_url,
        'api-key': gpn_key,
        'session_id': session_id,
        'Cookie': 'session-cookie=1758d005c3ff7477256ce8c118991a243e122dbe22a11716d5852fa58e676592a5af860934b4f64885ea6dc80d50e2ed'
    }
    body = {
        'user_id': vtk['tech_driver_id'],
        'pin': vtk['pin'],
        'device_id': 'xxxx',
        'device_name': 'Android1111'
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None


def get_vtk_barcode(card_num: str, token: str):
    """" проверка получение ШК ВТК"""

    vtk = get_vtk_info(card_num)

    # Проверяем компанию
    if vtk['azs_company_id'] == 1002:
        url = f'https://{barcode_api}/gpn'

    elif vtk['azs_company_id'] == 1000:
        url = f'https://{barcode_api}/rosneft'

    else:
        raise RuntimeError('Карта не ВТК!')

    headers = {
        'Content-Type': 'application/json',
        'Cookie': '53d4e18adf1674a3b93e63371b741a75=02e4c91cb6754b198c3303ec9b664f59; NSC_ESNS=2d5d4a6b-3031-13c9-9678-00e0ed6806e6_2011328032_1682857824_00000000000760926456',
        'Authorization' : f'Bearer {token}'
        }
    body = {
        'fuelCardNumber': vtk['card_num'],
        'vehicleNumber' : '"X999XX999"' # поле обязательное но сам номер значения не имеет
        }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None

def tech_drivers_dict():
    """собирает словарь тех спецов"""
    query = """SELECT "name", tech_driver_id FROM "core-azs".tech_driver"""
    resolve = db_request(query)
    res = {}
    for i in resolve:
        res[i['name']] = i['tech_driver_id']

    return res

def detach_card(card_num: str,  tech_driver_code: str, session_id: str):
    """отвязка от тех спеца"""
    vtk = get_vtk_info(card_num)
    url = f"""https://{gpn_url}/vip/v2/users/{tech_driver_code}/detachCard"""
    headers = {
        'Content-Type': 'application/json',
        'Host': gpn_url,
        'api-key': gpn_key,
        'session_id': session_id,
    }
    body = {
        'card_id' : vtk['card_id']
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None


def attach_card(card_num: str,  tech_driver_code: str, session_id: str):
    """привязка к тех спецу"""
    vtk = get_vtk_info(card_num)
    url = f"""https://{gpn_url}/vip/v2/users/{tech_driver_code}/attachCard"""
    headers = {
        'Content-Type': 'application/json',
        'Host': gpn_url,
        'api-key': gpn_key,
        'session_id': session_id,
    }
    body = {
        'card_id': vtk['card_id']
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None

def gpn_barcode_check(card_num: str,   session_id: str):
# Для получения ШК напрямую от ГПН

    vtk = get_vtk_info(card_num)
    card_id = vtk['card_id']
    url = f"""https://{gpn_url}/vip/v2/cards/{card_id}/pay"""
    headers = {
        'Content-Type': 'application/json',
        'api_key' : gpn_key,
        'session_id' : session_id,
        'contract_id': vtk['azs_contract_id']
    }
    body = {
        'pin' : vtk['pin']
    }


    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None

# print(tech_drivers_dict())

# auth = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxMSIsImp0aSI6IjAyYjEyYWUwZjg0MWYzYmZjMjI0MGQxMTU4MTM5NmRmNGQ2NzUzOTZiMjlhOTM3YWM4ODQzNDkxMDkyOTY4NTY4ZjQ2MmQxODkzZWJlODg5IiwiaWF0IjoxNzUwMDYwMDcwLjcwNzk2NywibmJmIjoxNzUwMDYwMDcwLjcwNzk2OSwiZXhwIjoxNzUyNjUyMDcwLjcwNDYzOCwic3ViIjoiMS0xMkRCV01ESCIsInNjb3BlcyI6W119.kbrFenYEvF2XNJ8EK_78S7BoW09uFZE3NBy4SFPFtAxud_WtndcOQZSYgsjt1aCvRRr9yFXUoSidQTofWBvmF8ukr-CcdN9kmphxKtmrmRBhPeF2TEugkzM_6d6uGrhJk7zf5JF57jWtoWXypuERTKIzNJv52USdWJumSsfRUJj4ypfljsYCZ9fUk0xwkjveuu7WQTk1q-ZAjh4zCdsHpMzbYr44lX3bAvkQoDXTpcBK_1VjIsRr03X5lsmcDm2nfWcsN2cu84WkcQZpheYdJ9bLS7l43HQS2h07Bz9RxCIygZovT7U64Awy3BbWJMtxHFEy8Bz7gQq_pKhV1J9uEAHzVJUQSjf5h1nYW6A81RQkaCfZJYmbfexwupK6RMP68yXJDR6hM8vmW476JW7dTDMe8kYH0vonKuqQxt4VxBkhbp0M8JtJ23HG-JwtOFkLUqNLQY2emtFM6mAq6zQ6aHnQHCjUPHLiLQYlSns-aSsmdUYKX7krwz599Arz4Uly9NtrcXgPWK1VB721uZhLYmSizpTxyMVdVMehZg4PrIOPExVrg5CI1DZ-dYP5SpOwbiM17CybXvfqoS8OcIU7XcFBy1KLEfX3QUvMmvwF3yTHwptwyISC0s778mWWhnaZTv1l8BZPGZCZLifhJdhPAdcpG3Qt0oNqTIy3AI58yd0'
# # # print(gpn_auth())
# # # #
# card_num = '7005830900981234'
# # # print(get_vtk_info(card_num))
# # # print(tabulate(DataFrame(get_vtk_info(card_num))))
# print(get_vtk_info(card_num)['azs_company_id'])
# try:
#     print(gpn_barcode_check(card_num, auth))
# except Exception as error:
#      print(error)



