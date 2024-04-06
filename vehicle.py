# -*- coding: utf-8 -*-
from x5t_connect import db_request

car_assign = "UPDATE \"core-vehicle-schema\".vehicle SET group_number='{0}' WHERE code = '{1}'"
car_drop = "UPDATE \"core-vehicle-schema\".vehicle SET group_number=NULL WHERE code = '{0}'"

def car_num_to_latin(car_num:str):
    #А, В, Е, К, М, Н, О, Р, С, Т, У и Х.
    ru_lat_dict = {'А':'A','В':'B','Е':'E','К':'K','М':'M','Н':'H','О':'O','Р':'P','С':'C','Т':'T','У':'Y','Х':'X'}
    res=car_num.upper()
    for i in range(len(res)):
        if res[i] in ru_lat_dict.keys():
            res = res.replace(res[i],ru_lat_dict[res[i]])
    return res

def group_list() -> list:
    group_list_query = """select distinct group_number 
                        from "core-vehicle-schema".vehicle order by group_number"""
    result = []
    for i in db_request(group_list_query):
        result.append(i['group_number'])
    return result

def vehicle_counter(code: str) -> int:
    counter = "select count(*) from \"core-vehicle-schema\".vehicle where code = \'{0}\'"
    return db_request(counter.format(code))[0]['count']


#print(car_num_to_latin('М959ут18'))