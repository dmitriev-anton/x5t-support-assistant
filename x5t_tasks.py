from datetime import datetime, date, time, timedelta
from x5t_connect import db_request
from invoice import auto_et_finish
import threading

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


vtk_bug_check = """select count(fc.number) from "core-vehicle-schema".fuel_cards fc 
                inner join "core-azs".vtk_request vr on vr.card_num like concat('%',fc.number::varchar) 
                where (fc.azs_company_id in (1000,1002)) and (fc.expiration_time >= now()) and fc.vtk = 0"""

vtk_bug = """update "core-vehicle-schema".fuel_cards fc set vtk = 1 where fc."number" in 
            (select fc.number from "core-vehicle-schema".fuel_cards fc
                inner join "core-azs".vtk_request vr on vr.card_num like concat('%',fc.number::varchar) 
                where (fc.azs_company_id in (1000,1002)) and (fc.expiration_time >= now()) and fc.vtk = 0)"""

sap_rejected_bug_check = """select invoice_id from "core-invoices-schema".own_trip where (status = 
'SAP_REJECTED') and sap_message like  ('%Обработка заявки типа%') """

sap_rejected_bug = """update "core-invoices-schema".own_trip set status  = 'SAP_CHECKED',driver_status = 'NEW', 
driver_version = 0 where (status = 'SAP_REJECTED') and sap_message like  ('%Обработка заявки типа%') """


def tasks():
    """Массовые фиксапдейты"""

    from datetime import datetime, date, time, timedelta
    #print('------------------------------------------------------------------------------------')
    print('Запуск бафера.')

    bad_ets = db_request(bad_et_check)
    if bad_ets != []:
        db_request(bad_et_upd)
        print(datetime.now(), "Баг некорректного начала порожних рейсов", bad_ets)

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
        print(datetime.now(), 'Баф по багу 1970 год', ids_1970)

    ets = auto_et_finish()
    #print(ets)
    if ets != []:
        print(datetime.now(),  'Завершение порожних рейсов', end='\t')
        print(ets)

    bad_vtk_counter = int(db_request(vtk_bug_check)[0]['count'])
    if bad_vtk_counter > 0:
        db_request(vtk_bug)
        print(datetime.now(), 'Исправление бага ВТК: ', bad_vtk_counter)

    sap_rejected_bug_counter = db_request(sap_rejected_bug_check)
    if sap_rejected_bug_counter != []:
        print(datetime.now(), 'Баг "Обработка заявки типа "Назначенная" не возможна" ', sap_rejected_bug_counter)
        db_request(sap_rejected_bug)
