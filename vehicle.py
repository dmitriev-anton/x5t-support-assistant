# -*- coding: utf-8 -*-

from x5t_connect_1line import db_request
# from x5t_connect import db_request

car_assign = "UPDATE \"core-vehicle-schema\".vehicle SET group_number='{0}' WHERE code = '{1}'"
car_drop = "UPDATE \"core-vehicle-schema\".vehicle SET group_number=NULL WHERE code = '{0}'"

def pretty_dict_print(my_dict : dict):
    # Находим максимальную длину ключа (в символах)
    max_key_len = max(len(str(key)) for key in my_dict)

    # Выводим элементы словаря с выравниванием
    for key, value in my_dict.items():
        print(f"{str(key):<{max_key_len}} : {value}")

def car_num_to_latin(car_num:str):
    #А, В, Е, К, М, Н, О, Р, С, Т, У и Х.
    ru_lat_dict = {'А':'A','В':'B','Е':'E','К':'K','М':'M','Н':'H','О':'O','Р':'P','С':'C','Т':'T','У':'Y','Х':'X'}
    res=car_num.upper()
    for i in range(len(res)):
        if res[i] in ru_lat_dict.keys():
            res = res.replace(res[i],ru_lat_dict[res[i]])
    return res

def group_list() -> tuple:
    group_list_query = """select distinct group_number 
                        from "core-vehicle-schema".vehicle order by group_number"""
    return [i['group_number'] for i in db_request(group_list_query)]

def vehicle_counter(code: str) -> int:
    counter = "select count(*) from \"core-vehicle-schema\".vehicle where code = \'{0}\'"
    return db_request(counter.format(code))[0]['count']

def search_wb_by_vehicle(veh_num :str):
    query = f"""select "number", system_status as system, user_status as user, vehicle_licence as vehicle, trailer_licence as trailer, driver_number as driver, 
    start_date_plan as plan_start,start_date_fact as fact_start ,end_date_plan as plan_end, "_type" as type from "core-waybills-schema".waybills where 
    vehicle_licence = '{veh_num}' order by start_date_plan desc limit 10"""
    return db_request(query)

def search_vehicle(veh_num :str):
    query = f"""select code, number, group_number as group, ut_code as ut,capacityton as tng, capacitypallet as plt, 
    motorcade, is_deleted from \"core-vehicle-schema\".vehicle where code like \'%{veh_num}%\'"""
    return db_request(query)

def fuel_cards_by_vehicle(vehicle: str):
    # поиск карт по ТС для 1 линии
    query = f"""select "number", company_id, azs_company_id, fuel_type, fuel_limit, expiration_time, vtk from 
    "core-azs".fuel_cards fc where code = '{vehicle}' """
    return db_request(query)

def asz_finder_ops_by_vehicle(vehicle: str):
    # подбор АЗС по номеру ТС
    query = f"""select uuid, driver_id, vehicle_code, created_at, "status", service_msg from 
    "core-azs".azs_finder_operations afo where vehicle_code = '{vehicle}' order by created_at desc limit 5"""
    return db_request(query)

def azs_finder_status(uuid: str):
    # статус АЗС по ЮИД
    query = f"""select azs_address, operation_uuid, is_select, price, discount_price, azs_company_id from 
    "core-azs".azs_finder_recommendations afr where operation_uuid = '{uuid}'"""
    # print(query)
    res = db_request(query)
    if res:
        return res[0]
    else:
        return None

# print(azs_finder_status('70585443-0d8b-4447-b1cb-64da04525548'))

# query = f"""select azs_address, operation_uuid, is_select, price, discount_price, azs_company_id from
#     "core-azs".azs_finder_recommendations afr where operation_uuid = '{uuid}'"""
# finder_status = azs_finder_status('70585443-0d8b-4447-b1cb-64da04525548')
# for key in finder_status.keys():
#     print(key + ':     ' + str(finder_status[key]))
