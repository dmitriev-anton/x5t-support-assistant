import PySimpleGUI as sg
import psycopg2
import psycopg2.extras


car_assign = "UPDATE \"core-vehicle-schema\".vehicle SET group_number='{0}' WHERE code = '{1}'";
car_drop = "UPDATE \"core-vehicle-schema\".vehicle SET group_number=NULL WHERE code = '{0}'";


layout = [[sg.Text('ВАЖНО!!!При вставке ТС раскладка должна быть английской!!!')], [sg.Text('Номер ТС(на латинице!)'), sg.InputText()],
    [sg.Checkbox('Аренда ТТ'), sg.Checkbox('Аренда Крафтер МФП'),
     sg.Checkbox('Аренда Крафтер УРАЛ'),sg.Checkbox('Убрать группу')],
    [sg.Submit('Применить'), sg.Cancel('Выход')], [sg.Output(size=(80, 15))]]

window = sg.Window('Привязка ТС для Х5Т Business Edition v2.1.0 by A.Dmitriev', layout)

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

result_string = 'ТС {1} привязано к группе {0}'

def vehicle_counter(code: str) -> int:
    counter = "select count(*) from \"core-vehicle-schema\".vehicle where code = \'{0}\'"
    return db_request(counter.format(code))[0]['count']

def main():
    while True:                             # The Event Loop
        event, values = window.read()
        #print(event, values) #debug
        vehicle_code = group = None
        if event in (None, 'Exit', 'Выход'):
           break

        elif event == 'Применить':
            vehicle_code = values[0].strip()
            if not values[0]:
                print('Отсутствует номер ТС.')

            elif vehicle_counter(vehicle_code) == 0:
                print('ТС {0} в системе х5транспорт отсутствует. Укажите существующий номер.'.format(vehicle_code))

            else:
                vehicle_code = values[0].strip()
                if values[1] and not values[2] and not values[3] and not values[4]:
                    print(result_string.format('Аренда ТТ', vehicle_code))
                    db_request(car_assign.format('Аренда ТТ', vehicle_code))

                elif values[2] and not values[1] and not values[3] and not values[4]:
                    print(result_string.format('Аренда Крафтер МФП', vehicle_code))
                    db_request(car_assign.format('Аренда Крафтер МФП', vehicle_code))

                elif values[3] and not values[1] and not values[2] and not values[4]:
                    print(result_string.format('Аренда Крафтер УРАЛ', vehicle_code))
                    db_request(car_assign.format('Аренда Крафтер УРАЛ', vehicle_code))

                elif values[4] and not values[1] and not values[2] and not values[3]:
                    print('Группа ТС {0} удалена'.format(vehicle_code))
                    db_request(car_drop.format(vehicle_code))

                else: print('Некорректный запрос!!!НЕЛЬЗЯ ПРИВЯЗАТЬ БОЛЕЕ ОДНОЙ ГРУППЫ!!!')


if __name__ == "__main__":
    main()

