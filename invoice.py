# -*- coding: utf-8 -*-
# from x5t_connect_1line import db_request
from x5t_connect import db_request
from typing import Union


total_insert = []


class Invoice:
    inv_req = "SELECT * from \"core-invoices-schema\".invoice where id = '{0}';"
    p_req = """SELECT * from "core-invoices-schema".invoice_unloading_points where invoice_id = '{0}' and invoice_system_version = '{1}' order by sequence"""
    plants_req = """select * FROM "core-plants-schema".plants where id = '{0}'"""
    points = []
    plants = []

    def __init__(self, invoice_id: int) -> None:
        self.invoice = db_request(self.inv_req.format(str(invoice_id)))[0]
        self.points = db_request(self.p_req.format(str(invoice_id), str(self.invoice['system_version'])))
        for i in self.points:
            self.plants.append(db_request(self.plants_req.format(i['internal_point_id'])))


def checkpoints_aio(inv: str) -> list:
    def insert_one_checkpoint(invoice: int, version: int, sequence: int, internal_point, external_point) -> str:

        """insert into "core-invoices-schema".driver_checkpoint (invoice_version, invoice_point_sequence, internal_point_id, external_point_id,'stage_id, create_time, invoice_id, credentials)
 values('2','2','Y982',unnest(array [1,4]),now(),'17026469','AUTOSET');"""

        # one_any_stage = """insert into \"core-invoices-schema\".driver_checkpoint (invoice_id, invoice_version, invoice_point_sequence, internal_point_id, external_point_id, stage_id, create_time, credentials) values('{0}','{1}','{2}','{3}','{4}',unnest(array [1,4]),now(),'AUTOSET');"""

        one_internal_point = """insert into \"core-invoices-schema\".driver_checkpoint (invoice_id, invoice_version, invoice_point_sequence, internal_point_id, stage_id, create_time, credentials) values('{0}','{1}','{2}','{3}', unnest(array [1,4]),now(),'AUTOSET');"""

        one_external_point = """insert into \"core-invoices-schema\".driver_checkpoint (invoice_id, invoice_version, invoice_point_sequence, external_point_id, stage_id, create_time, credentials) values('{0}','{1}','{2}', '{3}',unnest(array [1,4]),now(),'AUTOSET');"""

        if not external_point:
            return one_internal_point.format(str(inv), str(version), str(sequence), str(internal_point))
        elif not internal_point:
            return one_external_point.format(str(inv), str(version), str(sequence), str(external_point))

    result = []
    sequence = 0
    # print(type(inv))
    invoice=Invoice(inv)
    delete = """DELETE FROM "core-invoices-schema".driver_checkpoint where invoice_id = '{0}';""".format(str(invoice.invoice['id']))
    result.append(delete)

    for point in invoice.points:


        result.append(insert_one_checkpoint(str(invoice.invoice['id']), str(invoice.invoice['system_version']),
                                            str(sequence), point['internal_point_id'], point['external_point_id']))
        sequence += 1
    return result


# print(insert_one_checkpoint(1334, 1, 2, '0212', 1)

def update_status(invoice_id: str, status : str) -> None:

    # ot_driver_status = """select driver_status from "core-invoices-schema".own_trip where status in ('SAP_CHECKED',
    #     'PLANER_CHECKED','PLANNER_CONFIRMED') and driver_status in ('NEW', 'APPROVED', 'CHANGED') and invoice_id = '{0}'"""

    driver_status_upd = """update "core-drivers-schema".driver_status set STATUS = 'READY' 
                        where status in ('IN_TRIP','NOT_READY') and waybill_id in 
                        (select waybillid from "core-invoices-schema".own_trip 
                        where (status in ('SAP_CHECKED','PLANER_CHECKED','PLANNER_CONFIRMED', 'SAP_REJECTED')) 
                        and (driver_status in ('NEW', 'APPROVED','CHANGED')) and (invoice_id = '{0}'))"""

    finish_upd = """update "core-invoices-schema".own_trip set status = 'FINISHED', driver_status = 'APPROVED' where 
        status in ('SAP_CHECKED','PLANER_CHECKED','PLANNER_CONFIRMED','SAP_REJECTED') and invoice_id = '{0}'"""
    destr_upd = """update "core-invoices-schema".own_trip set status = 'DESTROYED', driver_status = 'CANCELED' where 
        status in ('SAP_CHECKED','PLANER_CHECKED','PLANNER_CONFIRMED','SAP_REJECTED') and invoice_id = '{0}'"""
    new_upd = """update "core-invoices-schema".own_trip set status = 'SAP_CHECKED', driver_status = 'NEW', sap_message = '' where 
        driver_status in ('APPROVED', 'NEW', 'CHANGED') and status in ('SAP_CHECKED','PLANER_CHECKED','PLANNER_CONFIRMED','SAP_REJECTED','FINISHED') and 
        invoice_id = '{0}'"""

    # try:
    #     trigger = db_request(ot_driver_status.format(invoice_id))[0]['driver_status']
    #     #print(trigger)
    # except IndexError:
    #     trigger = None
    #
    # if (trigger == 'APPROVED') or (trigger == 'CHANGED'):  ##### НОВАЯ ВЫБОРКА
    #     #rint(driver_status_upd.format(invoice_id))
    db_request(driver_status_upd.format(invoice_id))

    #print(own_trip_upd.format(invoice_id))
    if status == 'DESTROYED':
        db_request(destr_upd.format(invoice_id))
    elif status == 'FINISHED':
        db_request(finish_upd.format(invoice_id))
    elif status == 'NEW':
        db_request(new_upd.format(invoice_id))
    else:
        raise TypeError('Некорректный статус!')


def checkpoints(invoice_id:str) -> list:

    checkpoints_query = (
        "select invoice_version as inv_ver, invoice_point_sequence as seq, internal_point_id as int_p, "
        "external_point_id as ext_p, stage_id, create_time , longitude, latitude, "
        "credentials as creds FROM \"core-invoices-schema\".driver_checkpoint where invoice_id = '{0}' "
        "order by seq desc")
    temp = []
    temp = db_request(checkpoints_query.format(invoice_id))

    return temp


def search_invoice(inv_id: str):
    """Проба 1 запросом"""

    id = inv_id.strip().lstrip('0').upper()
    aio_num_q = (f'select id, sap_number, tms_number, expect_driver_date, plan_start_date, plan_end_date ,'
                 f'system_version, sap_version, sap_status_code as sap_code, is_mfp as mfp from '
                 f'\"core-invoices-schema\".invoice where id = \'{id}\' or tms_number = \'{id}\' or sap_number = '
                 f'\'00{id}\'')

    ltl_num_q = (f'select id, sap_number, tms_number, expect_driver_date, plan_start_date, plan_end_date ,'
                 f'system_version, sap_version, sap_status_code as sap_code, is_mfp as mfp from '
                 f'\"core-invoices-schema\".invoice where tms_number = \'{id}\'')

    tm_num_q = (f'select id, sap_number, tms_number, expect_driver_date, plan_start_date, plan_end_date ,'
                 f'system_version, sap_version, sap_status_code as sap_code, is_mfp as mfp from '
                 f'\"core-invoices-schema\".invoice where sap_number = \'{id}\'')

    # print(aio_num_q)

    try:
        if id[0] == 'L':
            x5tids = db_request(ltl_num_q)

        elif id[0] == 'T':
            x5tids = db_request(tm_num_q)

        else:
            x5tids = db_request(aio_num_q)
    except IndexError:
        return None
    return x5tids



def cure_invoice(invoice: str):
    """"""
    try:
        db_request(checkpoints_aio(invoice))
        return True
    except Exception as error:
        return error


def invoice_unloading_points(inv_id: str):
    """отчет по точкам рейса + координаты и активность из заводов."""
    query = (f'select iup.invoice_id, iup.invoice_system_version as \"version\", iup.\"sequence\", '
             f'concat(iup.internal_point_id, iup.external_point_id) as point_id,	iup.point_type,	iup.arrival_date_time, '
             f'iup.departure_date_time,	concat(p.latitude, ep.latitude) as latitude, concat(p.longitude, ep.longitude) '
             f'as longitude,(p.active or ep.active) as "active"	from "core-invoices-schema".invoice_unloading_points '
             f'iup left outer join "core-plants-schema".plants p on iup.internal_point_id = p.id left outer join '
             f'"core-plants-schema".external_plants ep on iup.external_point_id=ep.id where iup.invoice_id = \''
             f'{inv_id}\' order by iup.invoice_system_version')

    return db_request(query)

def cancel_asz(invoce_id: str):
    """"отменяет АЗС по инвойсу"""
    query = f"""update "core-azs".azs_finder_recommendations set is_select = false where operation_uuid in (
		select uuid from "core-azs".azs_finder_operations afo where invoice_id = '{invoce_id}' order by created_at desc)"""
    db_request(query)


def erase_action_sap(invoce_id: str):
    """Снимает зависшеее ожидание SAP"""
    query = f"""delete from "core-invoices-schema".invoice_action_sap where invoice_id = '{invoce_id}'"""
    db_request(query)

def get_own_trip(invoce_id: str):
    query = f"""select waybillid, version,"status", driver_status, driver_version, id, sap_message from "core-invoices-schema".own_trip where invoice_id = '{invoce_id}' order by version desc"""
    return db_request(query)



# print(auto_et_finish())
# inv_id = '12100439'
# print(get_x5t_id(inv_id))
#
# inv_id = '000050020367'
# print(inv_id.strip().lstrip('0'))
# print(get_x5t_id(inv_id))
#
# inv_id = '15510084'

# ot = get_own_trip_status('14475241')
# print(ot)
# print(ot[1]['waybillid'][2])

# cancel_asz('16028033')

# print(Invoice(16960788).points)

# for i in checkpoints_aio(17013078):
#     print(i)
