# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Union, Any

from x5t_connect import db_request

ot_check = "select id, driver_id, barcode, status, deleted from \"core-drivers-schema\".drivers_otvs where driver_id = (select id from " \
           "\"core-drivers-schema\".drivers where number = '{0}')"
ot_insrt = "insert into \"core-drivers-schema\".drivers_otvs (id,driver_id, deleted, status) values ((select max(" \
           "id)+1 from \"core-drivers-schema\".drivers_otvs), (select id from \"core-drivers-schema\".drivers where " \
           "number = '{0}'), 'false', 'CREATE')"
ot_upd = "update \"core-drivers-schema\".drivers_otvs set barcode = null, deleted = false, status = 'CREATE' where " \
         "driver_id = (select id from \"core-drivers-schema\".drivers where number = '{0}')"

auth_id_to_null = "UPDATE \"core-drivers-schema\".drivers set auth_user_id=NULL where number = '{0}'"


def default_features_set() -> list:
    dft_feature_dict_query = """SELECT feature_id FROM \"core-drivers-schema\".driver_type_features where driver_type = \'0\' order by feature_id """
    response = db_request(dft_feature_dict_query)
    return [i['feature_id'] for i in response]


def all_races(tab_num) -> list:
    active_pl_races = f"""select t4.id ,t4.sap_number as sap, t4.tms_number as tms, t2.status as sap_status, t2.driver_status as drv_status, 
                            t4.plan_start_date as plan_start,t5.status,t4.system_version as sys_ver, t2."version" as own_ver, 
                            t2.driver_version as dr_ver, t4.sap_status_code as sapCode, t4.is_mfp as mfp,t2.waybillid as PL
                            from "core-waybills-schema".waybills t3 
                            inner join "core-invoices-schema".own_trip t2 on t3."number"=t2.waybillid 
                            inner join "core-drivers-schema".driver_status t5 on t5.waybill_id = t2.waybillid 
                            inner join "core-invoices-schema".invoice t4 on t4.id=t2.invoice_id
                            where t3.driver_number = '{tab_num}' and t3.user_status = 'E0002' and t3.system_status = 'I0070' order by t4.plan_start_date ASC"""

    return db_request(active_pl_races)


def add_feature(tab_num: str, f_num: Union[str, list[str]]):
    add_feature = ("insert into \"core-drivers-schema\".driver_features (driver_id, feature_id) \n"
                   "	values ((select id from \"core-drivers-schema\".drivers where number = '{0}'),'{1}');")
    if type(f_num) == str:
        total_query = add_feature.format(tab_num, f_num)
        # print(total_query) check
    elif type(f_num) == list:
        total_query = [add_feature.format(tab_num, f) for f in f_num]

    try:
        db_request(total_query)
        return (f'Водителю {tab_num} добавлены фичи {f_num}')
    except Exception:
        print(total_query)
        return 'Невозможно добавить фичу!!!'


def remove_feature(tab_num: str, f_num=None):
    delete_feature = ('delete from "core-drivers-schema".driver_features '
                      f'where driver_id = (select id from "core-drivers-schema".drivers where number = \'{tab_num}\') '
                      f'and (feature_id = \'{f_num}\')')
    delete_all_features_query = (f'delete from "core-drivers-schema".driver_features where driver_id = (select id from '
                                 f'"core-drivers-schema".drivers where number = \'{tab_num}\')')

    if not f_num:
        total_query = delete_all_features_query
    else:
        total_query = delete_feature
    # print(total_query) check
    try:
        db_request(total_query)
        return f'Удаление фич водителю {tab_num}'
    except Exception as error:
        return error


def feature_dictionary():
    """кортеж всех фич"""
    feature_dictionary_query = """select id, "name", description from "core-drivers-schema".driver_feature_dictionary order by id"""
    return db_request(feature_dictionary_query)


def driver_features(tab_num) -> list:
    driver_features_query = """SELECT dr."number", df.feature_id, dfd.name, dfd.description  
                            FROM "core-drivers-schema".driver_features df 
                                inner join "core-drivers-schema".drivers dr on df.driver_id = dr.id
                                inner join "core-drivers-schema".driver_feature_dictionary dfd on dfd.id = df.feature_id 
                            where dr."number" = '{0}'"""
    temp = []

    temp = db_request(driver_features_query.format(tab_num))

    return temp


def driver_phone(num: str) -> Union[str, None]:
    driver_phone_query = 'select phone from "core-drivers-schema".drivers where number = \'{0}\''
    try:
        resolve = db_request(driver_phone_query.format(num))
        return resolve[0]['phone']
    except IndexError:
        return None


def search_driver(input: str) -> Union[object, list[Any]]:
    """Поиск по телефону или фио"""
    search_by_name = f"SELECT id, \"number\", \"name\", phone, ut, deleted, auth_user_id, status, \"type\", driver_id FROM \"core-drivers-schema\".drivers where name like \'%{input}%\'"
    search_by_phone = f"SELECT id, \"number\", \"name\", phone, ut, deleted, auth_user_id, status, \"type\", driver_id FROM \"core-drivers-schema\".drivers where phone like \'%{input}%\'"
    search_by_num = f"SELECT id, \"number\", \"name\", phone, ut, deleted, auth_user_id, status, \"type\", driver_id FROM \"core-drivers-schema\".drivers where \"number\" like \'%{input}%\'"
    result = []
    input=input.lstrip('X5T_')

    if input.isdigit() and len(input) == 10:
        return db_request(search_by_phone)

    elif input.replace(' ', '').isalpha():
        return db_request(search_by_name)

    elif input.isdigit() and (4 <= len(input) < 10) :
        return db_request(search_by_num)

    else:
        return []


def driver_waybills(num: str) -> list:
    """Путевые листы водителя"""
    waybills_query = ('select \"number\" as \"waybill\",system_status as system, user_status as user, '
                      'vehicle_licence as \"veh_num\", trailer_licence as \"trail_num\", '
                      'start_date_plan as \"plan_start\",end_date_plan as \"plan_end\", start_date_fact as \"fact_start\", '
                      'end_date_fact as \"fact_end\", is_mfp as \"mfp\" from \"core-waybills-schema\".waybills '
                      f'where driver_number = \'{num}\' order by start_date_plan desc limit 10')
    resolve = db_request(waybills_query)
    #print(waybills_query.format(num))
    return resolve


def driver_cards(num: str):
    fuel_cards_query = ('SELECT id, \"number\", code, company_id, azs_company_id, main, "fuel_type", fuel_limit, '
                        'create_time, vtk FROM \"core-azs\".fuel_cards '
                        'where (code in (\'{0}\', \'{1}\')) and (azs_company_id in (1000,1002)) '
                        'and (expiration_time >= now());')
    waybills = driver_waybills(num)
    real_start = None
    # print(waybills)
    # print(len(waybills))
    # print(len(waybills))
    res=[]
    for i in range(len(waybills)):

        if waybills[i]['system'] == 'I0070':

            res.append(waybills[i])
            # print(len(waybills))
            # print(wb)
            # print(res)

    counter = len(res)

    real_start = res[0]['plan_start']

    if counter == 1 and res[0]['fact_start']:
        real_start = res[0]['fact_start']
    elif counter == 1 and not res[0]['fact_start']:
        real_start = res[0]['plan_start']
    # print(waybills[0]['fact_start'])
    # print(real_start)
    if counter == 0:
        raise RuntimeError('Нет ПЛ со статусом в работе.')
    elif counter >= 2:
        raise RuntimeError('Более 1 ПЛ со статусом в работе.')
    elif real_start > datetime.now():
        raise RuntimeError('Начало ПЛ {0} {1} еще не наступило'.format(res[0]['waybill'], real_start))
    elif real_start and res[0]['plan_end'] < datetime.now():
        raise RuntimeError('ПЛ {0} истек {1}'.format(waybills[0]['waybill'], res[0]['plan_end']))
    else:
        # print(fuel_cards_query.format(waybills[0]['veh_num'], waybills[0]['trail_num']))
        vtks=db_request(fuel_cards_query.format(res[0]['veh_num'], res[0]['trail_num']))
        if not vtks: raise RuntimeError('Виртуальные карты к ТС не привязаны.')
        else: return vtks


def close_disp_inc(driver: str):
    """Закрывает все диспетчерские инциденты"""

    query = f"""update "core-incidents-schema".dispatching set status_id = '1004' where driver_number = '{driver}'"""
    db_request(query)

def get_last_user_agent(driver: str ):
    query = f"""select last_user_agent from "core-drivers-schema".drivers_user_agent where auth_id =  (select 
    auth_user_id from "core-drivers-schema".drivers where number = '{driver}')"""
    try:
        return db_request(query)
    except:
        return None


# print(feature_dictionary())
# print([i['id'] for i in feature_dictionary()])
# print(add_feature('00942766', '1044'))
# print(search_driver('02286799')[0]['auth_user_id'])
# print(auth_id_to_null.format('02286799'))
# db_request(auth_id_to_null.format('02286799'))
# print(search_driver('02286799')[0]['auth_user_id'])

# f25300be-5d5f-48b3-9e4f-9f3ba57414f3
# print(driver_cards('02029833'))
# print(all_races('02048874'))