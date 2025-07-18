# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras
import os
import sys
import logging
from pathlib import Path
import dotenv
from typing import Union


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='log.log',
    filemode='w'
)

def resource_path(relative_path):
    """Возвращает корректный путь для ресурсов в режиме PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Основная директория
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Пути к конфигурационным файлам
env_path = resource_path('.env')  # Для .env во временной директории
# config_path = os.path.join(base_dir, 'config.cfg')  # Для config.cfg рядом с EXE

logging.info(f"Base directory: {base_dir}")
logging.info(f".env path: {env_path}")
# logging.info(f"config.cfg path: {config_path}")

# Загрузка .env из ресурсов
if os.path.exists(env_path):
    dotenv.load_dotenv(dotenv_path=env_path, override=True)
    logging.info(".env loaded from resources")
else:
    logging.warning(".env not found in resources")

# # Загрузка config.cfg
# if os.path.exists(config_path):
#     dotenv.load_dotenv(dotenv_path=config_path, override=True)
#     logging.info("config.cfg loaded")
# else:
#     logging.error(f"config.cfg not found at {config_path}")

# Проверка переменных (добавьте свои)
required_vars = ['1LINE_DB_HOST', '1LINE_DB_USER', '1LINE_DB_PASSWORD', '1LINE_DB_NAME']
for var in required_vars:
    value = os.getenv(var)
    if value is None:
        logging.error(f"Missing variable: {var}")
    else:
        logging.info(f"{var} = {value if var != 'DB_PASSWORD' else '***'}")

# user=os.getenv("1LINE_DB_USER")
# password=os.getenv("1LINE_DB_PASSWORD")
# host=os.getenv("1LINE_DB_HOST")
# dbname=os.getenv("1LINE_DB_NAME")

user=os.getenv("DB_USER")
password=os.getenv("DB_PASSWORD")
host=os.getenv("DB_HOST")
dbname=os.getenv("DB_NAME")


# Проверка значений переменных
required_vars = ['1LINE_DB_HOST',  '1LINE_DB_USERNAME', '1LINE_DB_PASSWORD', '1LINE_DB_NAME']
for var in required_vars:
    value = os.getenv(var)
    if not value:
        logging.error(f"Missing environment variable: {var}")
    else:
        logging.info(f"{var} = {value if var != 'DB_PASSWORD' else '***'}")



def db_request(sql_request: Union[str, list[str]]) -> Union[list[dict], None]:
    """Шлат запрос или много запросов в зависимости от типа sql_request    """
    list_result = []
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)

    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:

            if type(sql_request) == str:
                    curs.execute(sql_request)
                    try:
                        ans = curs.fetchall()
                        for row in ans:
                            list_result.append(dict(row))
                        return list_result

                    except Exception as error:
                        return None

            elif type(sql_request) == list:
                try:
                    for r in sql_request:
                        curs.execute(r)
                    return None
                except Exception as error:
                    raise RuntimeError(error)
            else:
                raise RuntimeError('Incorrect request')


def str_dict(dict) -> str:
    result = ''
    for k in dict[0].keys():
        result += k
        result += ' '
    result += "\n"
    for i in dict:

        for k, v in i.items():
            result = result + str(v) + "  "

        result += "\n"

    return result


# _SQL = """select "number" , "name" , phone, licence, auth_user_id,
#     id, status, "type", driver_id, ut, birth_date, request_number, block_date
#     from "core-drivers-schema".drivers where number = '{0}'"""

# _SQL2 = """ select t1.phone,t2.waybillid as PL,t2.status,t2.driver_status,t4.sap_number,t2."version", t2.driver_version,t4.plan_start_date, t4.tms_number,t4.id,t3.is_mfp, t5.status
#     from "core-drivers-schema".drivers t1
#     inner join "core-waybills-schema".waybills t3 on t3.driver_number=t1."number" and t3.user_status = 'E0002' and t3.system_status = 'I0070'
#     inner join "core-invoices-schema".own_trip t2 on t3."number"=t2.waybillid
#     inner join "core-drivers-schema".driver_status t5 on t5.waybill_id = t2.waybillid
#     inner join "core-invoices-schema".invoice t4 on t4.id=t2.invoice_id
#     where t1."number" =  '{0}'"""

# _SQL3 = """SELECT df.feature_id,dfd."name", dfd.description  FROM "core-drivers-schema".driver_features df
#     inner join "core-drivers-schema".drivers dr on df.driver_id = dr.id
#     inner join "core-drivers-schema".driver_feature_dictionary dfd on dfd.id = df.feature_id
#     where dr.number = '{0}'"""
