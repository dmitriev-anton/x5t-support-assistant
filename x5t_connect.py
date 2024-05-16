import psycopg2
import psycopg2.extras
import os
import sys
from dotenv import load_dotenv

extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

def db_request(sql_request: str) -> object:
    """

    query function
    """
    dict_result = []
    conn = psycopg2.connect(dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USERNAME"),
                            password=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"))
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql_request)
    conn.commit()
    try:
        ans = cur.fetchall()
        for row in ans:
            dict_result.append(dict(row))
        return dict_result

    except psycopg2.ProgrammingError:
        return None

    cur.close()
    conn.close()



def get_dict_resultset(sql):
    conn = psycopg2.connect(dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USERNAME"),
                            password=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"))
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    ans = cur.fetchall()
    dict_result = []
    for row in ans:
        dict_result.append(dict(row))
    return dict_result

def str_dict(dict) -> str:
    result=''
    for k in dict[0].keys():
        result += k
        result += ' '
    result += "\n"
    for i in dict:

        for k, v in i.items():
            result = result + str(v) +  "  "

        result += "\n"

    return result



_SQL = """select "number" , "name" , phone, licence, auth_user_id, 
    id, status, "type", driver_id, ut, birth_date, request_number, block_date
    from "core-drivers-schema".drivers where number = '{0}'"""

_SQL2 = """ select t1.phone,t2.waybillid as PL,t2.status,t2.driver_status,t4.sap_number,t2."version", t2.driver_version,t4.plan_start_date, t4.tms_number,t4.id,t3.is_mfp, t5.status 
    from "core-drivers-schema".drivers t1
    inner join "core-waybills-schema".waybills t3 on t3.driver_number=t1."number" and t3.user_status = 'E0002' and t3.system_status = 'I0070'
    inner join "core-invoices-schema".own_trip t2 on t3."number"=t2.waybillid 
    inner join "core-drivers-schema".driver_status t5 on t5.waybill_id = t2.waybillid 
    inner join "core-invoices-schema".invoice t4 on t4.id=t2.invoice_id
    where t1."number" =  '{0}'"""

_SQL3 = """SELECT df.feature_id,dfd."name", dfd.description  FROM "core-drivers-schema".driver_features df 
    inner join "core-drivers-schema".drivers dr on df.driver_id = dr.id
    inner join "core-drivers-schema".driver_feature_dictionary dfd on dfd.id = df.feature_id 
    where dr.number = '{0}'"""







