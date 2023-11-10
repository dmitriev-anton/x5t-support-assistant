import PySimpleGUI as sg
import psycopg2
import psycopg2.extras


car_assign = "UPDATE \"core-vehicle-schema\".vehicle SET group_number='{0}' WHERE code = '{1}'";
car_drop = "UPDATE \"core-vehicle-schema\".vehicle SET group_number=NULL WHERE code = '{0}'";

assign_tab_layout = [[sg.Text('ТС'), sg.InputText(),sg.Text('Группа'), sg.InputText()],
    [sg.Checkbox('Аренда ТТ'), sg.Checkbox('Аренда Крафтер МФП'),
     sg.Checkbox('Аренда Крафтер УРАЛ'),sg.Checkbox('NULL')],
    [sg.Submit('Привязать'), sg.Cancel('Выход')],]

chkptr_tab_layout = [[sg.Text('Id_invoice'), sg.InputText()] ,[sg.Submit('Исправить'), sg.Cancel('Выход')]]

layout = [[sg.Text('ТС'), sg.InputText(),sg.Text('Группа'), sg.InputText()],
    [sg.Checkbox('Аренда ТТ'), sg.Checkbox('Аренда Крафтер МФП'),
     sg.Checkbox('Аренда Крафтер УРАЛ'),sg.Checkbox('NULL')],
    [sg.Submit('Привязать'), sg.Cancel('Выход')], [sg.Output(size=(103, 15))]]

window = sg.Window('Х5 transport assistant by A.Dmitriev', layout)

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

total_insert = []



while True:                             # The Event Loop
    event, values = window.read()
    #print(event, values) #debug
    vehicle_code = group = None
    if event in (None, 'Exit', 'Выход'):
        break

    elif event == 'Привязать':

        if not values[0]:
            print('Отсутствует номер ТС.')

        else:
            vehicle_code = values[0].strip()
            if values[2] and not values[1] and not values[5] and not values[3] and not values[4]:
                print(car_assign.format('Аренда ТТ', vehicle_code))
                db_request(car_assign.format('Аренда ТТ', vehicle_code))

            elif values[3] and not values[1] and not values[2] and not values[4] and not values[5]:
                print(car_assign.format('Аренда Крафтер МФП', vehicle_code))
                db_request(car_assign.format('Аренда Крафтер МФП', vehicle_code))

            elif values[4] and not values[1] and not values[2] and not values[3] and not values[5]:
                print(car_assign.format('Аренда Крафтер УРАЛ', vehicle_code))
                db_request(car_assign.format('Аренда Крафтер УРАЛ', vehicle_code))

            elif values[5] and not values[1] and not values[2] and not values[3] and not values[4]:
                print(car_drop.format(vehicle_code))
                db_request(car_drop.format(vehicle_code))

            elif values[1]and not values[5] and not values[2] and not values[3] and not values[4]:
                group = values[1].strip()
                print(car_assign.format(group, vehicle_code))
                db_request(car_assign.format(group, vehicle_code))

            else : print('Некорректный запрос!!!')

