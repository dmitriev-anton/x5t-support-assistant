

def all_races(tab_num) -> list:
    from x5t_connect import db_request

    active_pl_races = """  select t4.id,t4.sap_number, t4.tms_number as tms_num, t2."status" as sap_status, 
                            t2.driver_status,t4.plan_start_date,t5.status, t4.sap_status_code as sapCode, 
                                 t2.waybillid 
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


def driver_features(tab_num) -> list:
    from x5t_connect import db_request

    driver_features_query = """SELECT dr."number", df.feature_id, dfd.name, dfd.description  
                            FROM "core-drivers-schema".driver_features df 
                                inner join "core-drivers-schema".drivers dr on df.driver_id = dr.id
                                inner join "core-drivers-schema".driver_feature_dictionary dfd on dfd.id = df.feature_id 
                            where dr."number" = '{0}'"""
    temp = []
    temp = db_request(driver_features_query.format(tab_num))

    return temp




#for i in all_races('01764786'):
    #print(i)




