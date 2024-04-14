import requests

from x5t_connect import db_request
import psycopg2
from pandas import DataFrame
from tabulate import tabulate



ot_check = "select id, driver_id, barcode, status, deleted from \"core-drivers-schema\".drivers_otvs where driver_id = (select id from " \
           "\"core-drivers-schema\".drivers where number = '{0}')"
ot_insrt = "insert into \"core-drivers-schema\".drivers_otvs (id,driver_id, deleted, status) values ((select max(" \
           "id)+1 from \"core-drivers-schema\".drivers_otvs), (select id from \"core-drivers-schema\".drivers where " \
           "number = '{0}'), 'false', 'CREATE')"
ot_upd = "update \"core-drivers-schema\".drivers_otvs set barcode = null, deleted = false, status = 'CREATE' where " \
         "driver_id = (select id from \"core-drivers-schema\".drivers where number = '{0}')"
driver_phone_query = 'select phone from "core-drivers-schema".drivers where number = \'{0}\''

def all_races(tab_num) -> list:

    active_pl_races = """  select t4.id ,t4.sap_number as sap, t4.tms_number as tms, t2.status as sap_status, t2.driver_status, 
                            t4.plan_start_date as plan_start,t5.status,t4.system_version as sys_ver, t2."version" as own_ver, 
                            t2.driver_version as dr_ver, t4.sap_status_code as sapCode,  t3.is_mfp,  t2.waybillid as PL
                            from "core-drivers-schema".drivers t1
                            inner join "core-waybills-schema".waybills t3 on t3.driver_number=t1."number" 
                            and t3.user_status = 'E0002' and t3.system_status = 'I0070'
                            inner join "core-invoices-schema".own_trip t2 on t3."number"=t2.waybillid 
                            inner join "core-drivers-schema".driver_status t5 on t5.waybill_id = t2.waybillid 
                            inner join "core-invoices-schema".invoice t4 on t4.id=t2.invoice_id
                            where t1."number" = '{0}' order by t4.plan_start_date ASC"""
    temp = []
    temp = db_request(active_pl_races.format(tab_num))

    return temp

def add_feature(tab_num,f_num):
    add_feature = ("insert into \"core-drivers-schema\".driver_features (driver_id, feature_id) \n"
                   "	values ((select id from \"core-drivers-schema\".drivers where number = '{0}'),'{1}')")
    try:
        db_request(add_feature.format(tab_num,f_num))
        return('Фича {1} добавлена водителю {0}'.format(tab_num,f_num))
    except psycopg2.errors.UniqueViolation:
        return 'Невозможно добавить фичу!!!'

def remove_feature(tab_num,f_num):
    delete_feature = ('delete from "core-drivers-schema".driver_features '
                   'where driver_id = (select id from "core-drivers-schema".drivers where number = \'{0}\') '
                   'and (feature_id = \'{1}\')')
    try:
        db_request(delete_feature.format(tab_num,f_num))
        return('Фича {1} удалена у водителя {0}'.format(tab_num,f_num))
    except psycopg2.errors.UniqueViolation:
        return 'Невозможно удалить фичу!!!'

def feature_dictionary():
    feature_dictionary_query = """select id from "core-drivers-schema".driver_feature_dictionary order by id"""
    result = []
    response = db_request(feature_dictionary_query)
    for i in response:
        result.append(i['id'])
    return result


def driver_features(tab_num) -> list:

    driver_features_query = """SELECT dr."number", df.feature_id, dfd.name, dfd.description  
                            FROM "core-drivers-schema".driver_features df 
                                inner join "core-drivers-schema".drivers dr on df.driver_id = dr.id
                                inner join "core-drivers-schema".driver_feature_dictionary dfd on dfd.id = df.feature_id 
                            where dr."number" = '{0}'"""
    temp = []

    temp = db_request(driver_features_query.format(tab_num))

    return temp

def driver_phone(num: str):
    driver_phone_query = 'select phone from "core-drivers-schema".drivers where number = \'{0}\''
    try:
        resolve = db_request(driver_phone_query.format(num))
        return resolve[0]['phone']
    except IndexError:
        return None

#races = all_races('00642700')
#print(DataFrame(races))
#print(feature_dictionary())
#print(remove_feature('02017180','1043'))
#number = '900000301'
#print(driver_phone.format(number))
#print(driver_phone(number))