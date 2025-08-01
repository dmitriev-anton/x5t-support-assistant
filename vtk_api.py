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
              f'vr.azs_company_id, vr.card_id, vr.pin, vr.tech_driver_id, td."name", td.tech_driver_mobile as phone '
              f'FROM "core-azs".fuel_cards fc 	'
              f'left join "core-azs".vtk_request vr on cast(fc.number as text) = vr.card_num 	'
              f'left join "core-azs".tech_driver td on vr.tech_driver_id = td.tech_driver_id  '
              f'where fc.number = {card_num}')
    # print(_sql2)
    resolve = db_request(_sql2)
    # print(resolve)
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

    body = {
        'invoiceId': 201127,
        'fuelCardNumber': vtk['card_num'],
        'vehicleNumber': 'E050PT136',  # поле обязательное но сам номер значения не имеет
        'lat': 34.34,
        'lon': 34.34,
    }


    headers = {
        'Authorization': f'Bearer {token}',
        'Host': 'app-fleet.x5tmfp-prod-4.salt.x5.ru',
        'Content-Type': 'application/json',
        'Cookie': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjNTZmY2YzNC05MjAzLTRlNDItOGY1Ny1jMWE0OTI0Mzc2YTcifQ.eyJleHAiOjE3MTUxMjgxNDMsImlhdCI6MTcxNDg2ODk0MywianRpIjoiZGE3NDI1ODctMGY0MC00ZTU1LWJhYjgtNWUzZjk1ZDUxYzI3IiwiaXNzIjoiaHR0cHM6Ly9sb2dpc3RpY3MueDUucnUvYXV0aC9yZWFsbXMvbWZwcmVhbG0iLCJhdWQiOiJodHRwczovL2xvZ2lzdGljcy54NS5ydS9hdXRoL3JlYWxtcy9tZnByZWFsbSIsInN1YiI6IjZmOGZlZjhjLTkyOGQtNGE2Ni04YzJmLTgzMzZkZDllNjZhMCIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJhcHAtZmxlZXQtc2VydmljZSIsInNlc3Npb25fc3RhdGUiOiI1NmRiZWI2Yi0yN2M3LTRiZjktYmMzMy03ZTQ0M2E2YTJiMGMiLCJzY29wZSI6IiIsInNpZCI6IjU2ZGJlYjZiLTI3YzctNGJmOS1iYzMzLTdlNDQzYTZhMmIwYyJ9.CqtAQ5vSg2Myu5LPc4jG93JOICGH30WqDLeuJrcSzl8',
        # 'User-Agent': 'PostmanRuntime/7.44.1',

        }

    # print(headers)
    # print(body)

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


# # # print(gpn_auth())
# # # #

# print(get_vtk_info('7826010900001654698'))
# # # # print(tabulate(DataFrame(get_vtk_info(card_num))))
# print(get_vtk_info(card_num))

# token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJYeWhSclk4NTdWaTI4cEhvQXF1VUVuMTRKb2NOS0lYdUotT1JTMnlrLXZvIn0.eyJleHAiOjE3NTQxMjM3NTMsImlhdCI6MTc1NDAzNzM1MywianRpIjoib25ydHJvOjU1NzUyOWM5LWFmOGItNDdhNS05YjZjLTA0ZWM1MTVlNDExOSIsImlzcyI6Imh0dHBzOi8vbG9naXN0aWNzLng1LnJ1L2F1dGgvcmVhbG1zL21mcHJlYWxtIiwiYXVkIjpbImFwcC1mbGVldC1zZXJ2aWNlIiwiYXBwLW1pc3Npb24tY29udHJvbCIsImFjY291bnQiXSwic3ViIjoiMjNjZmU5NDItMDFmMi00Yjk4LThiYWQtODI4ODQ1NTI0ODcyIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYXBwLWZsZWV0LXNlcnZpY2UiLCJzaWQiOiIyYjg3MjAzZS0xMzJkLTRjNGItOTg0Yi1hM2MxMmQ4NGU5ZGYiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFwcC1mbGVldC1zZXJ2aWNlIjp7InJvbGVzIjpbIkRSSVZFUiJdfSwiYXBwLW1pc3Npb24tY29udHJvbCI6eyJyb2xlcyI6WyJESVNQQVRDSEVSIiwiVVNFUiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiIiLCJuYW1lIjoi0KDRg9Cx0LDQvdC-0LLQuNGHINCh0LXRgNCz0LXQuSDQn9C10YLRgNC-0LLQuNGHINCg0YPQsdCw0L3QvtCy0LjRhyDQodC10YDQs9C10Lkg0J_QtdGC0YDQvtCy0LjRhyIsInByZWZlcnJlZF91c2VybmFtZSI6IjkwNDU5MjEyNDkiLCJnaXZlbl9uYW1lIjoi0KDRg9Cx0LDQvdC-0LLQuNGHINCh0LXRgNCz0LXQuSDQn9C10YLRgNC-0LLQuNGHIiwiZmFtaWx5X25hbWUiOiLQoNGD0LHQsNC90L7QstC40Ycg0KHQtdGA0LPQtdC5INCf0LXRgtGA0L7QstC40YcifQ.KkV-HjdV4Um_XB9KRY2XtxTGcZkEeVC-T51cSkdXsFqcAZE6UdL50gpjZcwU6UCXZ3_UsInYs_WrcIkw5J8O8ZYwIEVhTx54e4hBXCgcm3GfKzeD1FgwzrHYDA9YfO-zJw1JM62HxxmCzXTV3IH9ORFxWwqUgrIwefUdrO8q5MAXwwYxLVgrtAxKMvB3jKroBXv62oyr5YJ-l3GPUNM_D9yqw93ZyCkmsjX26nCcd190f_WlO4zOMbD19Y0x1YKMWu4m27A5mDmDscgRujyJNRmJI2Dxlh74ruA5mghdol6-037G_EehwCI22jlRZWrPL7TFyBMdnJfPEP-rcYn4QQ'
# card_num = '7005830902184159'
# try:
#      print(get_vtk_barcode(card_num, token))
# except Exception as error:
#      print(error)



