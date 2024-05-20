# -*- coding: utf-8 -*-
import logging
import warnings

import PySimpleGUI as SG
from pandas import DataFrame
from tabulate import tabulate
from bee_sms import send_sms
from driver import *
from driver_api import driver_pwd_reset
from vtk_api import *
from invoice import Invoice, finish, checkpoints, checkpoints_aio, get_x5t_id, cure_invoice
from vehicle import car_num_to_latin, vehicle_counter, car_assign, car_drop
from x5t_connect import db_request
from x5t_tasks import tasks
from gui import main_window, f_dict


def main():
    warnings.filterwarnings('ignore')
    logging.basicConfig(
        level=logging.DEBUG,
        filename="log.log",
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(message)s",
        datefmt='%d-%m-%Y %H:%M:%S',
    )
    logging.info('Запуск приложения')

    window = main_window()  # вызов главного окна

    settings = {
        'driver_token': '',
        'gpn_session_id': '',
    }

    while True:  # The Event Loop

        event, values = window.read()

        if event in (SG.WIN_CLOSED, 'Exit'):
            break

        elif event == 'Привязать':
            print('------------------------------------------------------------------------------------')
            vehicle_code = car_num_to_latin(values['vehicle'].strip())
            window['vehicle'].update(vehicle_code)
            if not vehicle_code:
                print('Отсутствует номер ТС.')

            elif vehicle_counter(vehicle_code) == 0:
                print(f'ТС {vehicle_code} в системе х5транспорт отсутствует. Укажите существующий номер.')

            else:

                if not values['groups']:
                    db_request(car_drop.format(vehicle_code))
                    print(f'ТС {vehicle_code} отвязана.')
                    logging.info(f'ТС {vehicle_code} отвязана.')

                else:
                    db_request(car_assign.format(values['groups'], vehicle_code))
                    print('ТС {0} привязана к группе {1}.'.format(vehicle_code, values['groups']))
                    logging.info('ТС {0} привязана к группе {1}.'.format(vehicle_code, values['groups']))

        elif event == '-->X5T ID':
            # print('------------------------------------------------------------------------------------')
            # x5tid = None
            if not values['invoice_number'].strip():
                print('------------------------------------------------------------------------------------')
                print('Неверный номер!!!')
                # print(values)
            else:
                x5tid = get_x5t_id(values['invoice_number'].strip())
                if x5tid:
                    window['invoice_number'].update(x5tid)

                else:
                    print('------------------------------------------------------------------------------------')
                    print('Номер не найден!')

        elif event == 'Прожать':

            if not values['invoice_number'].strip():
                print('Введите номер рейса х5т')
            else:
                window.start_thread(lambda : cure_invoice(Invoice(int(values['invoice_number'].strip()))), '-cure_invoice-')

        elif event == '-cure_invoice-':
            print('------------------------------------------------------------------------------------')
            print('Рейс {0} прожат'.format(values['invoice_number']))
            logging.info('Рейс {0} прожат'.format(values['invoice_number']))

        elif event == 'Отменить':
            print('------------------------------------------------------------------------------------')
            if not values['invoice_number'].strip():
                print('Введите номер рейса х5т')
            else:
                finish(values['invoice_number'].strip(), True)
                print('Рейс {0} отменен'.format(values['invoice_number']))
                logging.info('Рейс {0} отменен'.format(values['invoice_number']))

        elif event == 'Завершить':
            print('------------------------------------------------------------------------------------')
            if not values['invoice_number'].strip():
                print('Введите номер рейса х5т')
            else:
                finish(values['invoice_number'].strip())
                print('Рейс {0} завершен'.format(values['invoice_number']))
                logging.info('Рейс {0} завершен'.format(values['invoice_number']))

        elif event == 'Бафнуть Х5Т':
            # print('Функционал отключен.')
            window.perform_long_operation(tasks, '-tasks-')
            logging.info('Запуск бафера')

        elif event == '-tasks-':
            print('--------------------------------------------------------------------------------------')
            print('Фиксы применены')

        elif event == 'Чекпоинты':
            print('-------------------------------------------------------------------------------------')
            if not values['invoice_number']:
                print('Введите номер рейса х5т')
            else:
                points = checkpoints(values['invoice_number'])
                if points:
                    points = DataFrame(points)
                    print(tabulate(points, headers='keys', tablefmt='tsv'))
                else:
                    print('Прожатия отсутствуют!')

        elif event == 'Поиск':
            print('------------------------------------------------------------------------------------')
            # print(values)
            if not values['driver_number'].strip():
                print('Введите данные для поиска.')
            else:
                drv = search_driver(values['driver_number'].strip())
                if not drv:
                    print('Водитель не найден')
                else:
                    if len(drv) == 1:
                        # если найден только 1 водитель подставлять табельный с нулями
                        # print(drv[0]['number'])
                        window['driver_number'].update(drv[0]['number'])

                    drv = DataFrame(drv)
                    # report = report_window('Поиск водителей', drv) # запускает новое окно табличного отчета
                    print(tabulate(drv, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))

        elif event == 'Путевые листы':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                waybills = driver_waybills(values['driver_number'].strip())
                if not waybills:
                    print('Путевые листы со статусом в работе отсутствуют.')
                else:
                    waybills = DataFrame(waybills)
                    print(tabulate(waybills, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))

        elif event == 'ВТК':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                try:
                    cards = driver_cards(values['driver_number'].strip())
                    cards = DataFrame(cards)
                    print(tabulate(cards, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))
                except RuntimeError as error:
                    print(error)

        elif event == 'Рейсы':
            # races = []
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                races = all_races(values['driver_number'].strip())

                if races:
                    races = DataFrame(races)
                    print(tabulate(races, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))
                else:
                    print('На активном ПЛ рейсы отсутствуют.')
                # report = report_window(sorted_races[0], sorted_races[1:])

        elif event == 'Фичи':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                # res = []
                features = driver_features(values['driver_number'])
                if not features:
                    print('У водителя дефолтный набор фич')
                else:
                    features = DataFrame(features)
                    print(tabulate(features, headers='keys', tablefmt='tsv'))

        elif event == 'Добавить фичу':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                # res = []
                features = driver_features(values['driver_number'])
                if not features:
                    print('У водителя дефолтный набор фич')
                else:
                    try:
                        # print(values['driver_number'], values['feature'])
                        res = add_feature(values['driver_number'], values['feature'])
                        print(res)
                        logging.info(res)
                    except Exception as error:
                        print(error)

        elif event == 'add_all':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                f4s = driver_features(values['driver_number'].strip())
                if not f4s:
                    res = add_feature(values['driver_number'].strip(), default_features_set())
                    print(res)
                    logging.info(res)
                else:
                    print('Добавление невозможно.У водителя уже присутствуют фичи.')

        elif event == 'remove_all':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                # res = []
                features = driver_features(values['driver_number'])
                if features:
                    res = remove_feature(values['driver_number'].strip())
                    print(res)
                    logging.info(res)
                else:
                    print('Удаление невозможно.У водителя отсутствуют фичи.')

        elif event == 'Удалить фичу':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                # res = []
                features = driver_features(values['driver_number'])

                if not features:
                    print('У водителя дефолтный набор фич')

                else:
                    try:
                        # print(values['driver_number'], values['feature_list'])
                        res = remove_feature(values['driver_number'], values['feature'])
                        print(res)
                        logging.info(res)
                    except Exception as error:
                        # print(values)
                        print(error)

        elif event == 'ШК ОТ/ВС':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                ot_id = db_request(ot_check.format(values['driver_number']))
                if not ot_id:
                    print('ШК ОТ/ВС отсутствует')
                else:
                    print(ot_id[0])
                    # print(tabulate(ot_id, headers='keys', tablefmt='tsv'))

        elif event == 'Обновить ШК ОТ/ВС':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                ot_id = db_request(ot_check.format(values['driver_number']))
                if not ot_id:
                    db_request(ot_insrt.format(values['driver_number']))
                    print('ШК ОТ/ВС водителя {0} прописан и поставлен на обновление.'.format(values['driver_number']))
                    logging.info('ШК ОТ/ВС водителя {0} прописан и поставлен на обновление.'.format(values['driver_number']))
                else:
                    db_request(ot_upd.format(values['driver_number']))
                    print('ШК ОТ/ВС водителя {0} поставлен на обновление.'.format(values['driver_number']))
                    logging.info('ШК ОТ/ВС водителя {0} поставлен на обновление.'.format(values['driver_number']))
                # event, values = window2.read()
                # window2.close()

        elif event == 'Токен':
            # print(values['driver_number'])
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Некорректный табельный номер')
            else:

                try:
                    window.start_thread(lambda: api_driver_token(phone), '-driver_token-')
                except Exception as token_error:
                    print(token_error)

        elif event == '-driver_token-':
            settings['driver_token'] = values['-driver_token-']
            print('------------------------------------------------------------------------------------')
            print('Токен водителя {0}-{1} загружен'.format(values['driver_number'].strip(), phone))
            logging.info('Токен водителя {0}-{1} загружен'.format(values['driver_number'].strip(), phone))
            logging.info(settings['driver_token'])
                    # print(settings['driver_token'])


        elif event == 'Сбросить пароль':
            # print(values['driver_number'])
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Некорректный табельный номер')
            else:
                window.start_thread(lambda :driver_pwd_reset(phone=phone), '-pwd_reset-')

        elif event == '-pwd_reset-':
            send_sms(phone)
            print('------------------------------------------------------------------------------------')
            print(f'Пароль водителя с телефоном {phone} сброшен. Смс о сбросе отправлено.')
            logging.info(f'Пароль водителя с телефоном {phone} сброшен. Смс о сбросе отправлено.')


        elif event == 'gpn_auth':
            window.start_thread(lambda: gpn_auth(), '-auth_done-')

        elif event == '-auth_done-':
            settings['gpn_session_id'] = values[event]
            print('------------------------------------------------------------------------------------')
            print('Сессия ГПН установлена')
            logging.info('Сессия ГПН установлена')
            logging.info(settings['gpn_session_id'])

        elif event == 'barcode':
            print('------------------------------------------------------------------------------------')
            if settings['driver_token'] and values['vtk'].strip():
                try:
                    response = get_vtk_barcode(values['vtk'].strip(), settings['driver_token'])
                    print(response)
                except Exception as error:
                    print(error)
            else:
                print('Токен не получен или отсутствует номер карты.')

        elif event == 'gpn_reset_counter':
            print('------------------------------------------------------------------------------------')
            if settings['gpn_session_id'] and values['vtk'].strip():
                print('Отправка запроса на сброс МПК карты {0}.'.format(values['vtk'].strip()))
                # print(values)
                try:
                    window.start_thread(lambda: gpn_reset_mpc(values['vtk'].strip(), settings['gpn_session_id']), '-gpn_reset_counter-')

                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты.')

        elif event == '-gpn_reset_counter-':
            print(values['-gpn_reset_counter-'])

        elif event == 'gpn_delete_mpc':
            print('------------------------------------------------------------------------------------')
            if settings['gpn_session_id'] and values['vtk'].strip():
                print('Отправка запроса на удаление карты {0}.'.format(values['vtk'].strip()))
                # print(values)
                try:
                    window.start_thread(lambda: gpn_delete_mpc(values['vtk'].strip(), settings['gpn_session_id']), '-gpn_delete_mpc-')
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты.')

        elif event == '-gpn_delete_mpc-':
            print(values['-gpn_delete_mpc-'])

        elif event == 'gpn_init_mpc':
            print('------------------------------------------------------------------------------------')
            if settings['gpn_session_id'] and values['vtk'].strip():
                print('Отправка запроса на выпуск карты {0}.'.format(values['vtk'].strip()))
                # print(values)
                try:
                    window.start_thread(lambda: gpn_init_mpc(values['vtk'].strip(), settings['gpn_session_id']), '-gpn_init_mpc-')
                    # print(response)
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты.')

        elif event == '-gpn_init_mpc-':
            print(values['-gpn_init_mpc-'])

        elif event == 'gpn_confirm_mpc':
            print('------------------------------------------------------------------------------------')
            if settings['gpn_session_id'] and values['vtk'].strip() and values['economist_code'].strip():
                print('Отправка кода экономиста.')
                # print(values)
                try:
                    window.start_thread(lambda: gpn_confirm_mpc(values['vtk'].strip(), values['economist_code'].strip(), settings['gpn_session_id']), '-gpn_confirm_mpc-')
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введены номер карты\код экономиста.')

        elif event == '-gpn_confirm_mpc-':
            print(values['-gpn_confirm_mpc-'])

        elif event == 'Отправить СМС':
            print('------------------------------------------------------------------------------------')
            # print(values)
            if values['sms_receiver'].strip().isdigit() and len(values['sms_receiver']) == 10 and values[
                'sms_body'] is not None:

                try:
                    send_sms(values['sms_receiver'].strip(), values['sms_body'].replace("\n", " "))
                    print('СМС отправлено на номер {0}'.format(values['sms_receiver'].strip()))
                    logging.info('СМС отправлено на номер {0}'.format(values['sms_receiver'].strip()))
                except Exception as error:
                    print(error)
            else:
                print('Некорректные данные! Перепроверьте правильность ввода!')


if __name__ == "__main__":
    main()
