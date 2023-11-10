# UPDATE "core-vehicle-schema".vehicle
# 	SET group_number='Аренда ТТ'
# 	WHERE code = 'T148AE761';
# Аренда ТТ
# Аренда Крафтер МФП
# Аренда Крафтер УРАЛ

import psycopg2
import psycopg2.extras

car_assign = "UPDATE \"core-vehicle-schema\".vehicle SET group_number='{0}' WHERE code = '{1}'";
car_drop = "UPDATE \"core-vehicle-schema\".vehicle SET group_number=NULL WHERE code = '{0}'";

def db_request(sql_request: str):
    dict_result = []
    conn = psycopg2.connect(dbname='mfp', user='anton_dmitriev',
                            password='PgVsMtcn@jd$AonUns', host='msk-dpro-psg044')
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


while 1 > 0:
    vehicle_code = input('Введите номер ТС(на латинице и без пробелов):').strip()
    if vehicle_code == 'exit':
        break
    print('Укажите группу (на латинице и без пробелов)')
    print('1 - Аренда ТТ, 2 - Аренда Крафтер МФП, 3 - Аренда Крафтер УРАЛ, 0 - NULL')
    group = input('Введите номер или название группы:').strip()

    if group == 'exit':
        break

    elif group =='0':
        print(car_drop.format(vehicle_code))
        db_request(car_drop.format(vehicle_code))

    elif group == '1':
        print(car_assign.format('Аренда ТТ', vehicle_code))
        db_request(car_assign.format('Аренда ТТ', vehicle_code))

    elif group == '2':
        print(car_assign.format('Аренда Крафтер МФП', vehicle_code))
        db_request(car_assign.format('Аренда Крафтер МФП', vehicle_code))

    elif group == '3':
        print(car_assign.format('Аренда Крафтер УРАЛ', vehicle_code))
        db_request(car_assign.format('Аренда Крафтер УРАЛ', vehicle_code))

    else:
        print(car_assign.format(group, vehicle_code))
        db_request(car_assign.format(group, vehicle_code))
