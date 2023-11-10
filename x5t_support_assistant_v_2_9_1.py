import PySimpleGUI as sg
import psycopg2
import psycopg2.extras
import logging
from x5t_connect import db_request
from invoice import Invoice, finish, checkpoints, checkpoints_aio, vehicle_counter, list_transform
from x5t_tasks import tasks
from get_group_list import group_list
from datetime import datetime, date, time, timedelta
from active_pl_races import all_races, driver_features
from reports_window import report_window
from bee_sms import send_sms

car_assign = "UPDATE \"core-vehicle-schema\".vehicle SET group_number='{0}' WHERE code = '{1}'"
car_drop = "UPDATE \"core-vehicle-schema\".vehicle SET group_number=NULL WHERE code = '{0}'"
ot_check = "select id from \"core-drivers-schema\".drivers_otvs where driver_id = (select id from " \
           "\"core-drivers-schema\".drivers where number = '{0}')"
ot_insrt = "insert into \"core-drivers-schema\".drivers_otvs (id,driver_id, deleted, status) values ((select max(" \
           "id)+1 from \"core-drivers-schema\".drivers_otvs), (select id from \"core-drivers-schema\".drivers where " \
           "number = '{0}'), 'false', 'CREATE')"
ot_upd = "update \"core-drivers-schema\".drivers_otvs set barcode = null, deleted = false, status = 'CREATE' where " \
         "driver_id = (select id from \"core-drivers-schema\".drivers where number = '{0}')"

sg.theme('DarkGreen5')


def main_window():
    chkptr_tab_layout = [[sg.Text('Id_invoice'), sg.InputText()],
                         [sg.Submit('Прожать'), sg.Submit('Отменить'), sg.Submit('Завершить'), sg.Submit('Бафнуть Х5Т'),
                          sg.Submit('Чекпоинты')]]

    new_tab_layout = [
        [sg.Text('ТС'), sg.InputText(), sg.Text('Группа'), sg.Combo(group_list(), default_value=group_list()[0]),
         sg.Submit('Привязать')]]

    drivers_tab_layout = [[sg.Text('Табельный номер'), sg.InputText(), sg.Submit('Показать рейсы'), sg.Submit('Фичи'),
                           sg.Submit('Обновить ШК ОТ/ВС')]]

    sms_tab_layout = [[sg.Text('Номер телефона'), sg.InputText(size=(12, 1)),sg.Submit('Отправить СМС')],
                      [sg.Text('СМС'), sg.InputText(size=(100, 2))]]

    main_layout = [[sg.TabGroup([[sg.Tab('Привязка ТС', new_tab_layout), sg.Tab('Рейсы', chkptr_tab_layout),
                                  sg.Tab('Водители', drivers_tab_layout), sg.Tab('SMS', sms_tab_layout)]])],
                                [sg.Output(size=(113, 15))]]

    return sg.Window('X5T support assistant v2.9.0 by A.Dmitriev', main_layout)


def main():
    start_time = datetime.now()
    logging.basicConfig(
        level=logging.DEBUG,
        filename="mylog.log",
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        datefmt='%H:%M:%S',
    )
    m_window = main_window()
    report = None

    while True:  # The Event Loop

        event, values = m_window.read()
        # print(event, values) #debug
        vehicle_code = group = None

        if event in (None, 'Exit', 'Выход'):
            break

        if event == 'Прожать':
            if not values[2].strip():
                print('Введите номер рейса х5т')
            else:
                cur_invoice = Invoice(int(values[2].strip()))
                cure = checkpoints_aio(cur_invoice)

                for i in cure:
                    db_request(i)
                # print(i)

                print('Рейс {0} исправлен'.format(values[2]))
                logging.info('Рейс {0} исправлен'.format(values[2]))

        if event == 'Отменить':
            if not values[2].strip():
                print('Введите номер рейса х5т')
            else:
                finish(values[2].strip(), True)
                print('Рейс {0} отменен'.format(values[2]))
                logging.info('Рейс {0} завершен'.format(values[2]))

        if event == 'Завершить':
            if not values[2].strip():
                print('Введите номер рейса х5т')
            else:
                finish(values[2].strip())
                print('Рейс {0} завершен'.format(values[2]))
                logging.info('Рейс {0} завершен'.format(values[2]))

        elif event == 'Привязать':
            vehicle_code = values[0].strip()
            if not vehicle_code:
                print('Отсутствует номер ТС.')

            elif vehicle_counter(vehicle_code) == 0:
                print('ТС {0} в системе х5транспорт отсутствует. Укажите существующий номер.'.format(vehicle_code))
                logging.info(
                    'ТС {0} в системе х5транспорт отсутствует. Укажите существующий номер.'.format(vehicle_code))

            else:
                if values[1] == None:
                    print(car_drop.format(vehicle_code))
                    db_request(car_drop.format(vehicle_code))
                    logging.info(car_drop.format(vehicle_code))

                else:
                    print(car_assign.format(values[1], vehicle_code))
                    db_request(car_assign.format(values[1], vehicle_code))
                    logging.info(car_assign.format(values[1], vehicle_code))

        if event == 'Бафнуть Х5Т':
            print('Функционал отключен.')
            #tasks()

        if event == 'Чекпоинты':
            print('------------------------------------------------------------------------------------')
            if not values[2]:
                print('Введите номер рейса х5т')
            else:
                points = checkpoints(values[2])
                for i in points:
                    for value in i.values():
                        print(value, end='\t')
                    print()

        if event == 'Показать рейсы' and report == None:
            print('------------------------------------------------------------------------------------')
            if not values[3]:
                print('Введите табельный номер')
            else:
                races = all_races(values[3])
                sorted_races = list_transform(races)
                print(sorted_races)
                # report = report_window(sorted_races[0], sorted_races[1:])

        if event == 'Фичи':
            print('------------------------------------------------------------------------------------')
            if not values[3]:
                print('Введите табельный номер')
            else:
                # res = []
                features = driver_features(values[3])
                for i in features:

                    for value in i.values():
                        print(value, end='\t')
                    print()
        #                    res.append(i.values)

        if event == 'Обновить ШК ОТ/ВС':
            print('------------------------------------------------------------------------------------')
            if not values[3]:
                print('Введите табельный номер')
            else:
                ot_id = db_request(ot_check.format(values[3]))
                #print(ot_id)
                #print(ot_insrt.format(values[3]))
                #print(ot_upd.format(values[3]))
                if ot_id == []:
                    db_request(ot_insrt.format(values[3]))
                    print('ШК ОТ/ВС водителя {0} прописан и поставлен на обновление.'.format(values[3]))
                else:
                    db_request(ot_upd.format(values[3]))
                    print('ШК ОТ/ВС водителя {0} поставлен на обновление.'.format(values[3]))
                # event, values = window2.read()
                # window2.close()
        if event == 'Отправить СМС':
            #print(values)
            print('------------------------------------------------------------------------------------')
            #print(len(values[4]))
            if values[4].isdigit() and len(values[4]) == 10 and values[5] != None:
                send_sms(values[4], values[5])
                print('СМС отправлено на номер {0}'.format(values[4]))
            else:
                print('Некорректные данные!!!Перепроверьте правильность ввода!')

    # window.close()


#        time_diff = datetime.now() - start_time
#      if time_diff >= timedelta(minutes=30):
#        start_time = datetime.now()
# tasks()


if __name__ == "__main__":
    main()
