# -*- coding: utf-8 -*-
import requests
import json
from x5t_connect import db_request
import os
from dotenv import load_dotenv


load_dotenv()
reg_api = os.getenv("DRIVER_REG_API")
info_api = os.getenv("DRIVER_INFO_API")


def driver_pwd_reset(phone: str) -> object:
    """Сброс пароля"""

    def api_pwd_recovery_request(phone: str):
        api = f'http://{reg_api}/api/v1/driver/password/recovery'

        headers = {
            'Content-Type': 'application/json',
            'Content-Length': '68',
            'Host': reg_api,
        }
        body = {
            'data': {'phone': phone},
            'params': 'null'
        }

        try:
            response = requests.post(api, headers=headers, data=json.dumps(body), timeout=30, verify=False)
            return response.json()['data']['verificationSessionId']
        except requests.exceptions.SSLError:
            return None

    def pwd_code(verification_id: str):
        _ = ('SELECT code FROM \"core-verification-schema\".phone_verification_session '
             'where status = \'ACTIVE\' and id = \'{0}\'')
        temp = None
        temp = db_request(_.format(verification_id))
        return temp[0]['code']

    def api_pwd_verify(code, phone, verification_id: str):

        api = f'http://{reg_api}/api/v1/driver/sms/verify'
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': '129',
            'Host': reg_api,
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
            return response.json()['data']['result']
        except requests.exceptions.SSLError:
            return None

    def api_pwd_create(password, verification_id: str):

        api = f'http://{reg_api}/api/v1/driver/password/create'
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': '122',
            'Host': reg_api,
        }
        body = {
            'data': {
                'password': password,
                'verificationSessionId': verification_id
            },
            'params': 'null'
        }
        try:
            response = requests.post(api, headers=headers, data=json.dumps(body), timeout=30, verify=False)
            return response.json()['data']['result']
        except requests.exceptions.SSLError:
            return None


    verification_id = api_pwd_recovery_request(phone)
    if verification_id:
        pass_code = pwd_code(verification_id)
        if api_pwd_verify(pass_code, phone, verification_id):
            result = api_pwd_create(password=phone[4:], verification_id=verification_id)
            if result: return True
            else:
                return 'Отказ на шаге 3'
        else:
            return 'Отказ на шаге 2'
    else:
        return 'Отказ на шаге 1'


def api_driver_token(phone: str) -> str:

    """Получает токен из БД или выдает ошибку"""

    api = f'https://{info_api}/v1/auth/drivers/token'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '17b4e09f4ad0242ff0dcd2969ae02791=5dc45d0378d1e3bd72bbffecd742833e',
        'User-Agent': 'X5 Transport NEW/123',
        #'Host': info_api,
    }
    body = {
        'password': phone[4:],
        'userName': phone
    }

    try:
        response = requests.post(api, headers=headers,data=json.dumps(body), verify=False).json()
        if response['data'] == None:
            raise RuntimeError(response['error']['message'])
        else:
            return response['data']['accessToken']

    except requests.exceptions.SSLError:
        raise ConnectionError('Ошибка связи.')




#print(api_driver_token('9898570346'))

