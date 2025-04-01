# -*- coding: utf-8 -*-
import requests
import json
from x5t_connect import db_request
import os
import sys
from dotenv import load_dotenv

extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))
reg_api = os.getenv("DRIVER_REG_API")
info_api = os.getenv("DRIVER_INFO_API")
app_fleet  = os.getenv("APP_FLEET")


def driver_pwd_reset(phone: str, password: str) -> object:
    """Сброс пароля"""

    def api_pwd_recovery_request(phone: str):
        api = f'http://{app_fleet}/info/v1/driver/password/recovery'

        headers = {
            'Content-Type': 'application/json',
            'Content-Length': '68',
            'Host': app_fleet,
            'User-Agent': 'X5 Transport NEW/versionName=25.3.20 versionCode=2503020',
        }
        body = {
            'data': {'phone': phone },
        }

        try:
            response = requests.post(api, headers=headers, data=json.dumps(body), timeout=30, verify=False)
            # print(response)
            return response.json()['data']['verificationSessionId']
        except requests.exceptions.SSLError:
            return None


    def pwd_code(verification_id: str):
        _ = ('SELECT code FROM \"core-verification-schema\".phone_verification_session '
             'where status = \'ACTIVE\' and id = \'{0}\'')
        temp = None
        temp = db_request(_.format(verification_id))
        print(temp)
        return temp[0]['code']

    def api_pwd_verify(code, phone, verification_id: str):

        api = f'http://{app_fleet}/info/v1/driver/sms/verify'
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': '129',
            'Host': app_fleet,
            'User-Agent': 'X5 Transport NEW/versionName=25.3.20 versionCode=2503020',
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
            'User-Agent': 'X5 Transport NEW/versionName=25.3.20 versionCode=2503020',
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

    verification_id = api_pwd_recovery_request(phone)
    if verification_id:
        pass_code = pwd_code(verification_id)
        if api_pwd_verify(pass_code, phone, verification_id):
            # password = ''.join(str(random.randint(0, 9)) for _ in range(6))
            result = api_pwd_create(phone=phone, password=password, verification_id=verification_id)
            if result:
                return True
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
        'User-Agent': 'X5 Transport NEW/versionName=24.3.20 versionCode=2503020',
        #'Host': info_api,
    }
    body = {
        'password': phone[4:],
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

# print(driver_pwd_reset('9110916360', '111112'))
