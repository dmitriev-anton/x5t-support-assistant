# -*- coding: utf-8 -*-
import requests
import psycopg2
import json
import time
from x5t_connect import db_request

def api_pwd_recovery_request(phone: str):
    api='http://app-registration.x5tmfp-prod-2.salt.x5.ru/api/v1/driver/password/recovery'

    headers = {
        'Content-Type': 'application/json',
        'Content-Length': '68',
        'Host': 'app-registration.x5tmfp-prod-2.salt.x5.ru',
               }
    body = {
        'data': {'phone': phone },
        'params': 'null'
            }

    try:
        response = requests.post(api, headers=headers,data=json.dumps(body),timeout=30,verify=False)
        return response.json()['data']['verificationSessionId']
    except requests.exceptions.SSLError:
        return None

def pwd_code(verification_id:str):
    _ = ('SELECT code FROM \"core-verification-schema\".phone_verification_session '
         'where status = \'ACTIVE\' and id = \'{0}\'')
    temp = None
    temp = db_request(_.format(verification_id))
    return temp[0]['code']

def api_pwd_verify(code, phone, verification_id : str):

    api = 'http://app-registration.x5tmfp-prod-2.salt.x5.ru/api/v1/driver/sms/verify'
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': '129',
        'Host': 'app-registration.x5tmfp-prod-2.salt.x5.ru',
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
        response = requests.post(api, headers=headers,data=json.dumps(body),timeout=30, verify=False)
        return response.json()['data']['result']
    except requests.exceptions.SSLError:
        return None

def api_pwd_create(password, verification_id : str):

    api = 'http://app-registration.x5tmfp-prod-2.salt.x5.ru/api/v1/driver/password/create'
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': '122',
        'Host': 'app-registration.x5tmfp-prod-2.salt.x5.ru',
               }
    body = {
        'data': {
            'password': password,
            'verificationSessionId': verification_id
                },
        'params': 'null'
            }
    try:
        response = requests.post(api, headers=headers,data=json.dumps(body),timeout=30, verify=False)
        return response.json()['data']['result']
    except requests.exceptions.SSLError:
        return None

def driver_pwd_reset(phone):
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


def api_pwd_recovery_request2(phone: str):
    api='http://app-registration.x5tmfp-prod-2.salt.x5.ru/api/v1/driver/password/recovery'

    headers = {
        'Content-Type': 'application/json',
        'Content-Length': '68',
        'Host': 'app-registration.x5tmfp-prod-2.salt.x5.ru',
               }
    body = {
        'data': {'phone': phone },
        'params': 'null'
            }

    response = requests.post(api, headers=headers,data=json.dumps(body),timeout=30, verify=False)
    return response.json()['data']['verificationSessionId']

#print(api_pwd_recovery_request2('9056000235'))
#print(driver_pwd_reset('9056000235'))