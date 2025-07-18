# -*- coding: utf-8 -*-
from x5t_connect import db_request
# from x5t_connect_1line import db_request


def search_waybill(wb: str):
    """ищет путевые листы"""
    waybills_query = f"""select "number", system_status as system, user_status as user, vehicle_licence as vehicle, trailer_licence as trailer, driver_number as driver, 
    start_date_plan as plan_start,start_date_fact as fact_start ,end_date_plan as plan_end, "_type" as type from "core-waybills-schema".waybills where 
    number like '%{wb}' order by start_date_plan desc limit 10"""

    # print(waybills_query)
    resolve = db_request(waybills_query)

    return resolve


def search_invoices_on_wb(wb: str):
    """покзаывает рейсы на путевом листе"""
    query = f""" select  t4.id, t4.sap_number, t4.tms_number as tms_num, t2.status as sap_status, t2.driver_status, 
        t4.plan_start_date, t4.system_version as sys_ver, t2."version" as own_ver, 
        t2.driver_version as dr_ver, t4.sap_status_code as sapCode,  t3.is_mfp,  t2.waybillid 
        from "core-waybills-schema".waybills t3 
        inner join "core-invoices-schema".own_trip t2 on t3."number"=t2.waybillid 
        inner join "core-invoices-schema".invoice t4 on t4.id=t2.invoice_id
        where t2.waybillid = '{wb}' order by t4.plan_start_date asc """

    resolve = db_request(query)
    return resolve

def wb_open_status(wb:str):
    """показывает логи открытия"""
    query = f"""select waybill_number, sap_request_status, err_message, create_datetime, source 
            from "core-waybills-schema".waybill_requests where waybill_number = '{wb}' """
    resolve = db_request(query)
    return resolve

def wb_open_log(wb:str):
    """показывает логи открытия"""
    query = f"""select waybill, sap_request_status, err_message, update_datetime, source 
            from "core-waybills-schema".waybill_requests_history where waybill = '{wb}' order by update_datetime desc limit 10"""
    resolve = db_request(query)
    return resolve

def wb_close_status(wb:str):
    """показывает логи закрытия"""
    query = f"""select waybill_number as waybill, sap_request_status, err_message , create_datetime , source
            from "core-waybills-schema".waybill_close_requests where waybill_number = '{wb}' 
                """
    resolve = db_request(query)
    return resolve

def wb_close_log(wb:str):
    """показывает логи закрытия"""
    query = f"""select waybill_number as waybill, sap_request_status, err_message , update_datetime , source
            from "core-waybills-schema".waybill_close_requests_history where waybill_number = '{wb}' 
            order by update_datetime desc limit 10"""
    resolve = db_request(query)
    return resolve

def close_wb(wb : str):
    """закрывает ПЛ в бд"""
    query = f"""update "core-waybills-schema".waybills set user_status = 'E0004', system_status = 'I0072' where number = '{wb}'"""
    db_request(query)

def briefing_report(wb : str):
    query = f"""SELECT ioi.driver_ext_id,ioi.driver_name, j.waybill_id, ioi.vehicle_license, i.type, ioc.type, ioc."result" , i.mechanic_id, i.created
                FROM "core-mech-schema".inspect i
                join "core-mech-schema".inspect_object_check ioc on i.id = ioc.inspect_id
                join "core-mech-schema".inspect_objects_info ioi on i.id = ioi.inspect_id
                join "core-mech-schema".journal j on j.id = i.journal_id
                where j.waybill_id  = '{wb}'
                order by i.created desc"""
    return  db_request(query)

# print(wb_open_status('VG0000251080'))
# print(wb_close_status('NN0000298725'))