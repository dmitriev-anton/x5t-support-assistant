



def auto_et_finish()-> list:
    from x5t_connect import db_request
    from invoice import finish
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
            finish(i['invoice_id'])
            res.append(i['invoice_id'])

    return res


#print(auto_et_finish())