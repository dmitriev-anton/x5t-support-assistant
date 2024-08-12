# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta
from x5t_connect import db_request
from invoice import update_status

bad_et_check = """select id from "core-invoices-schema".invoice where type_code = 'ET' and plan_start_date between (
now() - interval '2 day') and (NOW() + interval '1 day') and expect_driver_date < plan_start_date """

bad_et_upd = """update "core-invoices-schema".invoice set expect_driver_date = plan_start_date where type_code = 'ET' 
and plan_start_date between (now() - interval '2 day') and (NOW() + interval '1 day') and expect_driver_date < 
plan_start_date """

bug_1970_check = """select id from "core-invoices-schema".invoice where plan_start_date = '1970-01-01 03:00:00.000'"""

bug_1970 = """update "core-invoices-schema".invoice set plan_start_date = expect_driver_date 
            where (plan_start_date = '1970-01-01 03:00:00.000')"""

bug_1970_id= """update "core-invoices-schema".invoice set plan_start_date = expect_driver_date 
            where (plan_start_date = '1970-01-01 03:00:00.000')and id = '{0}'"""


vtk_bug_check = """select count(fc.number) from "core-azs".fuel_cards fc 
                inner join "core-azs".vtk_request vr on vr.card_num like concat('%',fc.number::varchar) 
                where (fc.azs_company_id in (1000,1002)) and (fc.expiration_time >= now()) and fc.vtk = 0"""

vtk_bug = """update "core-azs".fuel_cards fc set vtk = 1 where fc."number" in 
            (select fc.number from "core-azs".fuel_cards fc
                inner join "core-azs".vtk_request vr on vr.card_num like concat('%',fc.number::varchar) 
                where (fc.azs_company_id in (1000,1002)) and (fc.expiration_time >= now()) and fc.vtk = 0)"""

sap_rejected_bug_check = """select invoice_id from "core-invoices-schema".own_trip where (status = 
'SAP_REJECTED') and sap_message like  ('%Обработка заявки типа%') """

sap_rejected_bug = """update "core-invoices-schema".own_trip set status  = 'SAP_CHECKED',driver_status = 'NEW', 
driver_version = 0 where (status = 'SAP_REJECTED') and sap_message like  ('%Обработка заявки типа%') """

def auto_et_finish()-> list:

    from datetime import datetime, date, time, timedelta
    actual_et_ids = """select invoice_id from "core-invoices-schema".own_trip where status = 'PLANER_CHECKED' 
                    and driver_status in ('APPROVED','NEW') and invoice_id in 
                    (select id from "core-invoices-schema".invoice where type_code = 'ET' 
                        and plan_start_date between (now() - interval '2 day') and NOW() order by plan_start_date)"""

    counter_et_ids = """select count(invoice_id) from "core-invoices-schema".own_trip where status = 'PLANER_CHECKED' 
                        and driver_status in ('APPROVED','NEW') and invoice_id in 
                        (select id from "core-invoices-schema".invoice where type_code = 'ET' 
                            and plan_start_date between (now() - interval '2 day') and NOW() order by plan_start_date)"""

    temp = db_request(actual_et_ids)
    res = []

    if int(db_request(counter_et_ids)[0]['count']) > 0:

        #print(datetime.now(), 'Порожние рейсы')
        for i in temp:
            update_status(i['invoice_id'], 'FINISH')
            res.append(i['invoice_id'])

    return res

def tasks():
    """Массовые фиксапдейты"""

    from datetime import datetime, date, time, timedelta
    #print('------------------------------------------------------------------------------------')
    # result = ''
    # print('Запуск бафера.')

    bad_ets = db_request(bad_et_check)
    if bad_ets != []:
        db_request(bad_et_upd)

    ids_1970 = []
    counter = 0
    ids_1970 = db_request(bug_1970_check)
    #print(ids_1970 != [])
    #print(ids_1970)
    if ids_1970 != []:
        #print(ids_1970)
        for i in ids_1970:
            counter+=1
            #print(i['id'], end='\t')
            db_request(bug_1970_id.format(i['id']))
            #print(bug_1970_id.format(i['id']))
            #print(db_request(bug_1970_id.format(i['id'])))

    ets = auto_et_finish()
    #print(ets)
    # if ets != []:
    #     print(datetime.now(),  'Завершение порожних рейсов', end='\t')
    #     print(ets)

    bad_vtk_counter = int(db_request(vtk_bug_check)[0]['count'])
    if bad_vtk_counter > 0:
        db_request(vtk_bug)


    sap_rejected_bug_counter = db_request(sap_rejected_bug_check)
    if sap_rejected_bug_counter != []:
        db_request(sap_rejected_bug)

