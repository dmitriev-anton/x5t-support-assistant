# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
import requests
import psycopg2
import json
import time
import asyncio
from x5t_connect import db_request
from driver_api import api_driver_token

load_dotenv()
gpn_login = os.getenv("GPN_LOGIN")
gpn_pwd = os.getenv("GPN_PWD")
gpn_url = os.getenv("GPN_URL")
gpn_key = os.getenv("GPN_API_KEY")


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
        return response.json()['data']['session_id']
    except requests.exceptions.SSLError:
        return None

def get_vtk_info(card_num:str):
    _sql = (f'SELECT id, request_id, azs_contract_id, request_date, request_status, end_date, card_num, parent_id, '
           f'vtk_create_time, error_msg, azs_company_id, card_id, pin, confirm_mpc, tech_driver_id, card_status FROM '
           f'\"core-azs\".vtk_request where card_num = \'{card_num}\'')

    resolve = db_request(_sql)
    if resolve:
        return resolve[0]
    else:
        raise RuntimeError('Карта в таблице ВТК не обнаружена.')

def gpn_delete_mpc(card_num:str, session_id:str):

    """удаление МПК ГПН"""

    vtk = get_vtk_info(card_num)

    url = "https://{0}/vip/v2/cards/{1}/deleteMPC".format(gpn_url, vtk['card_id'])

    headers = {
        'contract_id': vtk['contract_id'],
        'Content-Type': 'application/json',
        'Host': gpn_url,
        'api-key': gpn_key,
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
    url = "https://{0}/vip/v2/cards/{1}/initMPC".format(gpn_url, vtk['card_id'])

    headers = {
        'contract_id': vtk['contract_id'],
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': gpn_url,
        'api-key': gpn_key,
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

    url = "https://{0}/vip/v2/cards/{1}/confirmMPC".format(gpn_url, vtk['card_id'])
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'contract_id': vtk['contract_id'],
        'Host': gpn_url,
        'api-key': gpn_key,
        'session_id': session_id,
        'Cookie': cookie
        }

    body = {
        'code': economist_code
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        return response.json()
    except requests.exceptions.SSLError:
        return None


def gpn_update_mpc(card_num: str, session_id: str):
    """обновление мпк"""


    vtk = get_vtk_info(card_num)

    url = "https://{0}/vip/v2/cards/{1}/resetMPC?type = ResetCounterMPC".format(gpn_url, vtk['card_id'])

    headers = {
        'contract_id': vtk['contract_id'],
        'Content-Type': 'application/x-www-form-urlencoded',
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


#auth = gpn_auth()
#print(auth)

# card_num = '7005830901024257'
# print(get_vtk_info(card_num))

