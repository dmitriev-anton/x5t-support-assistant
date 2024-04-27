import logging
import warnings

import PySimpleGUI as sg
from pandas import DataFrame
from tabulate import tabulate

from bee_sms import send_sms
from driver import *
from driver_api import driver_pwd_reset
from invoice import Invoice, finish, checkpoints, checkpoints_aio, get_x5t_id
from vehicle import car_num_to_latin, group_list, vehicle_counter, car_assign, car_drop
from x5t_connect import db_request
from x5t_tasks import tasks

f_dict=feature_dictionary()
g_list=group_list()



def main_window():
    sg.theme('DarkGreen5')
    invoice_tab_layout = [
        [sg.Text('Id_invoice'), sg.InputText(), sg.Submit('-->X5T ID')],
        [sg.Submit('Прожать'), sg.Submit('Отменить'), sg.Submit('Завершить'), sg.Submit('Чекпоинты'),
         sg.Submit('Бафнуть Х5Т')]
    ]

    vehicle_tab_layout = [
        [sg.Text('ТС'), sg.InputText(), sg.Text('Группа'), sg.Combo(g_list, default_value=g_list[0], readonly=True),
         sg.Submit('Привязать')]
    ]

    drivers_tab_layout = [
        [sg.Text('Таб.н.'), sg.InputText(), sg.Submit('Поиск'), sg.Submit('Рейсы'), sg.Submit('Путевые листы'),sg.Submit('ВТК'),sg.Submit('Сбросить пароль')],
        [sg.Submit('Фичи'),sg.Combo(f_dict, default_value=f_dict[0], readonly=True), sg.Submit('Добавить фичу'),sg.Submit('Удалить фичу'),sg.Submit('ШК ОТ/ВС'), sg.Submit('Обновить ШК ОТ/ВС'), ]
    ]

    cards_tab_layout = []

    sms_tab_layout = [
        [sg.Multiline(default_text='Введите текст сообщения', size=(80, 3), no_scrollbar=True),
         sg.InputText(default_text='Номер телефона', size=(15, 3)),
         sg.Submit('Отправить СМС')]
    ]

    main_layout = [
        [sg.TabGroup([[sg.Tab('Привязка ТС', vehicle_tab_layout), sg.Tab('Рейс', invoice_tab_layout),
            sg.Tab('Водители', drivers_tab_layout), sg.Tab('ВТК', cards_tab_layout), sg.Tab('SMS', sms_tab_layout)]])],
        [sg.Output(size=(140, 20))]
    ]

    return sg.Window('X5T support assistant v2.14 by A.Dmitriev', main_layout)


def main():
    warnings.filterwarnings('ignore')
    logging.basicConfig(
        level=logging.DEBUG,
        filename="log.log",
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(message)s",
        datefmt='%d-%m-%Y %H:%M:%S',
    )
    logging.info('Запуск приложения')
    m_window = main_window()

    while True:  # The Event Loop

        event, values = m_window.read()
        vehicle_code = group = None

        if event in ('Exit', 'Выход',sg.WIN_CLOSED):
            break

        if event == 'Привязать':
            print('------------------------------------------------------------------------------------')
            vehicle_code = car_num_to_latin(values[0].strip())
            m_window[0].update(vehicle_code)
            if not vehicle_code:
                print('Отсутствует номер ТС.')

            elif vehicle_counter(vehicle_code) == 0:
                print(f'ТС {vehicle_code} в системе х5транспорт отсутствует. Укажите существующий номер.')

            else:

                if values[1] == None:
                    db_request(car_drop.format(vehicle_code))
                    print(f'ТС {vehicle_code} отвязана.')
                    logging.info(f'ТС {vehicle_code} отвязана.')

                else:
                    db_request(car_assign.format(values[1], vehicle_code))
                    print(f'ТС {vehicle_code} привязана к группе {values[1]}.')
                    logging.info(f'ТС {vehicle_code} привязана к группе {values[1]}.')

        if event == '-->X5T ID':
            #print('------------------------------------------------------------------------------------')
            x5tid = None
            if not values[2].strip():
                print('------------------------------------------------------------------------------------')
                print('Неверный номер!!!')
                #print(values)

            else:
                x5tid = get_x5t_id(values[2].strip())
                if x5tid:
                    m_window[2].update(x5tid)

                else:
                    print('------------------------------------------------------------------------------------')
                    print('Номер не найден!')


        if event == 'Прожать':
            print('------------------------------------------------------------------------------------')
            if not values[2].strip():
                print('Введите номер рейса х5т')
            else:
                cur_invoice = Invoice(int(values[2].strip()))
                cure = checkpoints_aio(cur_invoice)

                for i in cure:
                    db_request(i)
                # print(i)

                print(f'Рейс {values[2]} прожат')
                logging.info(f'Рейс {values[2]} прожат')

        if event == 'Отменить':
            print('------------------------------------------------------------------------------------')
            if not values[2].strip():
                print('Введите номер рейса х5т')
            else:
                finish(values[2].strip(), True)
                print(f'Рейс {values[2]} отменен')
                logging.info(f'Рейс {values[2]} отменен')

        if event == 'Завершить':
            print('------------------------------------------------------------------------------------')
            if not values[2].strip():
                print('Введите номер рейса х5т')
            else:
                finish(values[2].strip())
                print(f'Рейс {values[2]} завершен')
                logging.info(f'Рейс {values[2]} завершен')


        if event == 'Бафнуть Х5Т':
            #print('Функционал отключен.')
            tasks()
            logging.info('Запуск бафера')

        if event == 'Чекпоинты':
            print('--------------------------------------------------------------------------------------')
            if not values[2]:
                print('Введите номер рейса х5т')
            else:
                points = checkpoints(values[2])
                if points != []:
                    points = DataFrame(points)
                    print(tabulate(points, headers='keys', tablefmt='tsv'))
                else:
                    print('Прожатия отсутствуют!')

        if event == 'Поиск':
            print('------------------------------------------------------------------------------------')
            if not values[3].strip():
                print('Введите данные для поиска.')
            else:
                drv = search_driver(values[3].strip())
                if drv == []:
                    print('Водитель не найден')
                else:
                    drv = DataFrame(drv)
                    print(tabulate(drv, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))

        if event == 'Путевые листы' :
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                waybills = driver_waybills(values[3].strip())
                if waybills == []:
                    print('Путевые листы со статусом в работе отсутствуют.')
                else:
                    waybills=DataFrame(waybills)
                    print(tabulate(waybills, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))
        if event == 'ВТК' :
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                try:
                    cards = driver_cards(values[3].strip())
                    cards = DataFrame(cards)
                    print(tabulate(cards, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))
                except RuntimeError as error:
                    print(atr(error))

        if event == 'Рейсы' :
            races = []
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                races = all_races(values[3].strip())

                if races != []:
                    races= DataFrame(races)
                    print(tabulate(races, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))
                else:
                    print('На активном ПЛ рейсы отсутствуют.')
                # report = report_window(sorted_races[0], sorted_races[1:])

        if event == 'Фичи':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3])
            if not phone:
                print('Водитель не найден.')
            else:
                # res = []
                features = driver_features(values[3])
                if features == []:
                    print('У водителя дефолтный набор фич')
                else:
                    features = DataFrame(features)
                    print(tabulate(features, headers='keys', tablefmt='tsv'))

        if event == 'Добавить фичу':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3])
            if not phone:
                print('Водитель не найден.')
            else:
                # res = []
                features = driver_features(values[3])
                if features == []:
                    print('У водителя дефолтный набор фич')

                elif values[4] not in f_dict:
                    print('Внимание!Некорректная фича!')

                else:
                    res = add_feature(values[3],values[4])
                    print(res)
                    logging.info(res)


        if event == 'Удалить фичу':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3])
            if not phone:
                print('Водитель не найден.')
            else:
                # res = []
                features = driver_features(values[3])
                if features == []:
                    print('У водителя дефолтный набор фич')

                elif values[4] not in f_dict:
                    print('Внимание!Некорректная фича!')

                else:
                    res = remove_feature(values[3],values[4])
                    print(res)
                    logging.info(res)

        if event == 'ШК ОТ/ВС':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3])
            if not phone:
                print('Водитель не найден.')
            else:
                ot_id = db_request(ot_check.format(values[3]))
                if ot_id == []:
                    print('ШК ОТ/ВС отсутствует')
                else:
                    print(ot_id[0])
                    #print(tabulate(ot_id, headers='keys', tablefmt='tsv'))

        if event == 'Обновить ШК ОТ/ВС':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3])
            if not phone:
                print('Водитель не найден.')
            else:
                ot_id = db_request(ot_check.format(values[3]))
                if ot_id == []:
                    db_request(ot_insrt.format(values[3]))
                    print(f'ШК ОТ/ВС водителя {values[3]} прописан и поставлен на обновление.')
                    logging.info(f'ШК ОТ/ВС водителя {values[3]} прописан и поставлен на обновление.')
                else:
                    db_request(ot_upd.format(values[3]))
                    print(f'ШК ОТ/ВС водителя {values[3]} поставлен на обновление.')
                    logging.info(f'ШК ОТ/ВС водителя {values[3]} поставлен на обновление.')
                # event, values = window2.read()
                # window2.close()

        if event == 'Сбросить пароль':
            print('------------------------------------------------------------------------------------')
            #print(values[3])
            phone = driver_phone(values[3])
            if not phone:
                print('Некорректный табельный номер')
            else:
                rst_result = driver_pwd_reset(phone=phone)
                if rst_result == True:
                    send_sms(phone)
                    print(f'Пароль водителя с телефоном {phone} сброшен. Смс о сбросе отправлено.')
                    logging.info(f'Пароль водителя с телефоном {phone} сброшен. Смс о сбросе отправлено.')
                else:
                    print(rst_result)


        if event == 'Отправить СМС':
            #print(values)
            print('------------------------------------------------------------------------------------')
            #print(len(values[4]))
            if values[6].isdigit() and len(values[6]) == 10 and values[6] != None:

                send_sms(values[6], values[5].replace("\n", " "))
                #print(values[5].replace("\n", " "))
                print(f'СМС отправлено на номер {values[6]}')
                logging.info(f'СМС отправлено на номер {values[6]}')
            else:
                print('Некорректные данные!!!Перепроверьте правильность ввода!')

if __name__ == "__main__":
    main()
