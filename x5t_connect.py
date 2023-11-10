import psycopg2
import psycopg2.extras
from flask import Flask, session, json, jsonify, render_template, request, escape, copy_current_request_context
#from checker import check_logged_in

app=Flask(__name__)

db_cfg = {'host': 'v1-nx-psg0153',
          'user': 'anton_dmitriev',
          'password' : 'PgVsMtcn@jd$AonUns',
          'dbname': 'mfp', }

def db_request(sql_request: str) -> object:
    dict_result = []
    conn = psycopg2.connect(dbname='mfp', user='anton_dmitriev',
                            password='PgVsMtcn@jd$AonUns', host='v1-nx-psg0153')
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
    conn = psycopg2.connect(dbname='mfp', user='anton_dmitriev',
                        password='PgVsMtcn@jd$AonUns', host='msk-dpro-psg044')
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


# conn = psycopg2.connect(dbname='mfp', user='anton_dmitriev',
#                        password='PgVsMtcn@jd$AonUns', host='msk-dpro-psg044')
# cursor = conn.cursor()
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

#tab_num = """'00638577'"""




#for k, v in current_races[0].items(): print(k, end=' ')
#print()
#for i in current_races:
#    for k, v in i.items():
 #       print(v, end=' ')
#    print()


#print(current_races)
#print()
#print()

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':

    return render_template('entry.html',
                           the_title='Welcome to x5transport support on the web!')

@app.route('/search', methods=['POST'])
def do_search() -> 'html':
    tab_num = request.form['tabnum']
    title = 'fucking results'
    driver_info = get_dict_resultset(_SQL.format(tab_num))
    current_races = get_dict_resultset(_SQL2.format(tab_num))
    driver_features = get_dict_resultset(_SQL3.format(tab_num))
    output = str_dict(driver_info) + "\n\n" + str_dict(current_races) + "\n\n" + str_dict(driver_features)
    titles1 = []
    data1 = []
    for k, v in driver_info[0].items():
        titles1.append(str(k))
        data1.append(str(v))



    print(titles1)
    print(data1)

    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles1,
                           the_data=data1)

@app.route('/driver_info')
def driver_page() -> str:
    output = str_dict(driver_info) + "\n\n" + str_dict(current_races)+ "\n\n" + str_dict(driver_features)

    print(output)
    return output

app.secret_key = 'SimplePasskey'

if __name__ == '__main__':
    app.run(debug=True)
