from x5t_connect import db_request

total_insert = []

def vehicle_counter(code: str) -> int:
    counter = "select count(*) from \"core-vehicle-schema\".vehicle where code = \'{0}\'"
    return db_request(counter.format(code))[0]['count']

class Invoice:

    inv_req = "SELECT * from \"core-invoices-schema\".invoice where id = '{0}';"
    p_req = """SELECT * from "core-invoices-schema".invoice_unloading_points where invoice_id = '{0}' and invoice_system_version = '{1}' order by sequence"""
    plants_req = """select * FROM "core-plants-schema".plants where id = '{0}'"""
    points =[]
    plants = []

    def __init__(self, invoice_id: int) -> None:

        self.invoice = db_request(self.inv_req.format(str(invoice_id)))[0]
        self.points = db_request(self.p_req.format(str(invoice_id), str(self.invoice['system_version'])))
#            self.points.append(i['internal_point_id'])
        for i in self.points:
            self.plants.append(db_request(self.plants_req.format(i['internal_point_id'])))
 #       for plant in self.points: self.plants.append(db_request(self.plants_req.format()))

#        print(self.p_req.format(str(invoice_id), str(self.invoice['system_version'])))


def checkpoints_aio(invoice: Invoice) -> list:
    def insert_one_checkpoint(invoice: int, version: int, sequence: int, internal_point: str, external_point:str, stage_num: int) -> str:
        one_internal_stage = ('INSERT INTO "core-invoices-schema".driver_checkpoint '
                     '(invoice_id, invoice_version, invoice_point_sequence, internal_point_id, external_point_id,'
                     'stage_id, create_time, id, longitude, latitude, credentials, username)'
                     'VALUES     ({0}, {1}, {2}, \'{3}\', NULL, {4},now(), (select(max(id) + 1) FROM '
                     '"core-invoices-schema".driver_checkpoint),'
                     '0, 0, \'AUTOSET\', null);')

        one_external_stage = ('INSERT INTO "core-invoices-schema".driver_checkpoint '
                              '(invoice_id, invoice_version, invoice_point_sequence, internal_point_id, external_point_id,'
                              'stage_id, create_time, id, longitude, latitude, credentials, username)'
                              'VALUES     ({0}, {1}, {2}, NULL, \'{3}\', {4},now(), (select(max(id) + 1) FROM '
                              '"core-invoices-schema".driver_checkpoint),'
                              '0, 0, \'AUTOSET\', null);')

        if not external_point:
            return one_internal_stage.format(str(invoice), str(version), str(sequence), internal_point, str(stage_num))
        elif not internal_point:
            return one_external_stage.format(str(invoice), str(version), str(sequence), external_point, str(stage_num))
    result = []
    sequence = 0
    delete = """DELETE FROM "core-invoices-schema".driver_checkpoint where invoice_id = \'{0}\' ;""".format(str(invoice.invoice['id']))
    result.append(delete)

    for point in invoice.points:
        for stage in range(1, 5):
            result.append(insert_one_checkpoint(str(invoice.invoice['id']),
                                                str(invoice.invoice['system_version']),
                                                str(sequence), point['internal_point_id'], point['external_point_id'], str(stage),
                                                ))

        sequence += 1
    return result


# print(insert_one_checkpoint(1334, 1, 2, '0212', 1)

def finish(invoice_id, to_destroy=False) -> None:
    from x5t_connect import db_request

    ot_driver_status = """select driver_status from "core-invoices-schema".own_trip where status in ('SAP_CHECKED','PLANER_CHECKED','PLANNER_CONFIRMED') and driver_status in ('NEW', 'APPROVED') and invoice_id = '{0}'"""

    driver_status_upd = """update "core-drivers-schema".driver_status set STATUS = 'READY' 
                        where status in ('IN_TRIP','NOT_READY') and waybill_id in 
                        (select waybillid from "core-invoices-schema".own_trip 
                        where (status in ('SAP_CHECKED','PLANER_CHECKED','PLANNER_CONFIRMED')) 
                        and (driver_status in ('NEW', 'APPROVED','CHANGED')) and (invoice_id = '{0}'))"""

    own_trip_upd = """update "core-invoices-schema".own_trip set status = 'FINISHED', driver_status = 'APPROVED' where status in ('SAP_CHECKED','PLANER_CHECKED','PLANNER_CONFIRMED','SAP_REJECTED') and invoice_id = '{0}'"""
    destr_upd = """update "core-invoices-schema".own_trip set status = 'DESTROYED', driver_status = 'CANCELED' where status in ('SAP_CHECKED','PLANER_CHECKED','PLANNER_CONFIRMED','SAP_REJECTED') and invoice_id = '{0}'"""

    try:
        trigger = db_request(ot_driver_status.format(invoice_id))[0]['driver_status']
        #print(trigger)
    except IndexError:
        trigger = None


    if (trigger == 'APPROVED') or (trigger == 'CHANGED'): ##### НОВАЯ ВЫБОРКА
        #rint(driver_status_upd.format(invoice_id))
        db_request(driver_status_upd.format(invoice_id))

    #print(own_trip_upd.format(invoice_id))
    if to_destroy == True:
        db_request(destr_upd.format(invoice_id))
    else:
        db_request(own_trip_upd.format(invoice_id))


def checkpoints(invoice_id) -> list:
    from x5t_connect import db_request

    checkpoints_query = """select * FROM "core-invoices-schema".driver_checkpoint where invoice_id = '{0}'"""
    temp = []
    temp = db_request(checkpoints_query.format(invoice_id))

    return temp

def list_transform(input: list) -> list:
    output = []

    if input != []:
        headers = [k for k in input[0].keys()]
        output.append(headers)
        for i in input:
            temp = []
            for c in i.values():
                temp.append(c)
            output.append(temp)
    return output






#cur_invoice = Invoice(7224907)

#print(cur_invoice.invoice)
#print(cur_invoice.invoice['system_version'])
#print(cur_invoice.invoice['id'])
#print(cur_invoice.points)
#print(cur_invoice.plants)

#cure = checkpoints_aio(cur_invoice)

#for i in cure:
    #db_request(i)
    #print(i)

#print('Готово')

#print(vehicle_counter('X897AX761'))

finish(10629383)