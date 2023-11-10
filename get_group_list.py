from x5t_connect import db_request

def group_list() -> list:
    group_list_query = """select distinct group_number 
                        from "core-vehicle-schema".vehicle order by group_number"""
    result = []
    for i in db_request(group_list_query):
        result.append(i['group_number'])

    return result


#print(group_list())