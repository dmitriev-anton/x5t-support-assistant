# -*- coding: utf-8 -*-
import logging
import os
import warnings

import PySimpleGUI as SG
from pandas import DataFrame
from tabulate import tabulate
from bee_sms import send_sms
from driver import *
from driver_api import driver_pwd_reset
from vtk_api import *
from invoice import *
from vehicle import *
from x5t_connect import db_request
from x5t_tasks import tasks
from gui import main_window, f_dict


def main():
    warnings.filterwarnings("ignore")  # игнор ненужных уведомлений

    username = os.getlogin()  # получаем логин юзера
    logging.basicConfig(
        level=logging.DEBUG,
        filename="log.log",
        format=f'%(asctime)s - {username} - %(module)s - %(levelname)s : %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S',
    )
    logging.info('Запуск приложения')

    window = main_window()  # вызов главного окна

    delimiter = '-' * 160  # разделитель для вывода
    settings = {  # хранение токенов для запросов
        'driver_token': '',
        'gpn_session_id': '',
    }
    tablefmt = "plain"  # 'simple', 'tsv' - подходят

    while True:  # The Event Loop

        event, values = window.read()

        if event in (SG.WIN_CLOSED, 'Exit'):
            break

        elif event == 'Привязать':
            print(delimiter)
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

        elif event == 'Искать ПЛ':
            print(delimiter)
            vehicle_code = car_num_to_latin(values['vehicle'].strip())
            window['vehicle'].update(vehicle_code)
            if not vehicle_code:
                print('Отсутствует номер ТС.')

            elif vehicle_counter(vehicle_code) == 0:
                print(f'ТС {vehicle_code} в системе х5транспорт отсутствует. Укажите существующий номер.')

            else:
                wbs = search_wb_by_vehicle(values['vehicle'])
                if wbs:
                    print(tabulate(DataFrame(wbs), headers='keys', tablefmt=tablefmt))
                else:
                    print('Путевые листы не найдены')


        elif event == '-->X5T ID':
            print(delimiter)
            if not values['invoice_number'].strip():
                print('Неверный номер!!!')
            else:

                x5tids = search_invoice(values['invoice_number'].strip())
                if len(x5tids) == 1:
                    window['invoice_number'].update(x5tids[0]['id'])
                    print(tabulate(DataFrame(x5tids), headers='keys', tablefmt=tablefmt))

                elif len(x5tids) > 1:
                    print(tabulate(DataFrame(x5tids), headers='keys', tablefmt=tablefmt))

                else:
                    print('Номер не найден!')

        elif event == 'ПЛ ТМ Фикс':
            if not values['invoice_number'].strip():
                print(delimiter)
                print('Введите номер рейса х5т')
            else:
                try:
                    cure_own_trip_tm_invoice(values['invoice_number'].strip())
                    print(delimiter)
                    print('Замена ПЛ ТМ по рейсу {0} выполнена.'.format(values['invoice_number'].strip()))
                    logging.info('Замена ПЛ ТМ по рейсу {0} выполнена.'.format(values['invoice_number'].strip()))
                except Exception as error:
                    print(delimiter)
                    print(error)

        elif event == 'Снять АЗС':

            if not values['invoice_number'].strip():
                print(delimiter)
                print('Введите номер рейса х5т')
            else:
                try:
                    cancel_asz(values['invoice_number'].strip())
                    print(delimiter)
                    print('Подбор АЗС по рейсу {0} снят.'.format(values['invoice_number'].strip()))
                    logging.info('Подбор АЗС по рейсу {0} снят.'.format(values['invoice_number'].strip()))
                except Exception as error:
                    print(error)

        elif event == 'Убрать Ожидание SAP':
            if not values['invoice_number'].strip():
                print(delimiter)
                print('Введите номер рейса х5т')

            else:
                try:
                    erase_action_sap(values['invoice_number'].strip())
                    print(delimiter)
                    print('Ожидание SAP по рейсу {0} снятo.'.format(values['invoice_number'].strip()))
                    logging.info('Ожидание SAP по рейсу {0} снятo.'.format(values['invoice_number'].strip()))
                except Exception as error:

                    print(error)

        elif event == 'Прожать':

            if not values['invoice_number'].strip():
                print('Введите номер рейса х5т')
            else:
                window.start_thread(lambda: cure_invoice(Invoice(int(values['invoice_number'].strip()))),
                                    '-cure_invoice-')
                print(delimiter)
                print('Запуск в фоновом режиме. Дождитесь выполнения операции.')

        elif event == '-cure_invoice-':
            print(delimiter)
            print('Рейс {0} прожат'.format(values['invoice_number']))
            logging.info('Рейс {0} прожат'.format(values['invoice_number']))

        elif event == 'Изменить':
            print(delimiter)

            if not values['invoice_number'].strip():
                print('Введите номер рейса х5т')
            else:
                try:
                    update_status(values['invoice_number'].strip(), values['status'])
                    print('Рейсу {0} присвоен статус {1}'.format(values['invoice_number'], values['status']))
                    logging.info('Рейсу {0} присвоен статус {1}'.format(values['invoice_number'], values['status']))

                except TypeError as error:
                    print(error)

        elif event == 'Бафнуть Х5Т':
            # print('Функционал отключен.')
            window.perform_long_operation(tasks, '-tasks-')
            print(delimiter)
            print('Запуск бафера')
            logging.info('Запуск бафера')

        elif event == '-tasks-':
            print(delimiter)
            print('Фиксы применены')

        elif event == 'Прожатия':
            print(delimiter)
            if not values['invoice_number']:
                print('Введите номер рейса х5т')
            else:
                points = checkpoints(values['invoice_number'])
                if points:
                    print(tabulate(DataFrame(points), headers='keys', tablefmt=tablefmt))
                else:
                    print('Прожатия отсутствуют!')

        elif event == 'Точки':
            print(delimiter)
            if not values['invoice_number']:
                print('Введите номер рейса х5т')
            else:
                stages = invoice_unloading_points(values['invoice_number'])
                if stages:
                    print(tabulate(DataFrame(stages), headers='keys', tablefmt=tablefmt))
                else:
                    print('Некорректный номер рейса!')

        elif event == 'Поиск':
            print(delimiter)
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
                        window['sms_receiver'].update(drv[0]['phone'])
                    # report = report_window('Поиск водителей', drv) # запускает новое окно табличного отчета
                    print(tabulate(DataFrame(drv), headers='keys', showindex=False, tablefmt=tablefmt, numalign='left'))

        elif event == 'Путевые листы':
            print(delimiter)
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                waybills = driver_waybills(values['driver_number'].strip())
                if not waybills:
                    print('Путевые листы со статусом в работе отсутствуют.')
                else:
                    print(tabulate(DataFrame(waybills), headers='keys', showindex=False, tablefmt=tablefmt,
                                   numalign='left'))

        elif event == 'ВТК':
            print(delimiter)
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                try:
                    cards = driver_cards(values['driver_number'].strip())
                    print(
                        tabulate(DataFrame(cards), headers='keys', showindex=False, tablefmt=tablefmt, numalign='left'))
                except RuntimeError as error:
                    print(error)

        elif event == 'Рейсы':
            # races = []
            print(delimiter)
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                races = all_races(values['driver_number'].strip())

                if races:
                    print(
                        tabulate(DataFrame(races), headers='keys', showindex=False, tablefmt=tablefmt, numalign='left'))
                else:
                    print('На активном ПЛ рейсы отсутствуют.')
                # report = report_window(sorted_races[0], sorted_races[1:])

        elif event == 'Фичи':
            print(delimiter)
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                # res = []
                features = driver_features(values['driver_number'])
                if not features:
                    print('У водителя дефолтный набор фич')
                else:
                    print(tabulate(DataFrame(features), headers='keys', tablefmt=tablefmt))

        elif event == 'Добавить фичу':
            print(delimiter)
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
            print(delimiter)
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
            print(delimiter)
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
            print(delimiter)
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
            print(delimiter)
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                ot_id = db_request(ot_check.format(values['driver_number']))
                if not ot_id:
                    print('ШК ОТ/ВС отсутствует')
                else:
                    print(ot_id[0])
                    # print(tabulate(ot_id, headers='keys', tablefmt=tablefmt))

        elif event == 'Обновить ШК ОТ/ВС':
            print(delimiter)
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                ot_id = db_request(ot_check.format(values['driver_number']))
                if not ot_id:
                    db_request(ot_insrt.format(values['driver_number']))
                    print('ШК ОТ/ВС водителя {0} прописан и поставлен на обновление.'.format(values['driver_number']))
                    logging.info(
                        'ШК ОТ/ВС водителя {0} прописан и поставлен на обновление.'.format(values['driver_number']))
                else:
                    db_request(ot_upd.format(values['driver_number']))
                    print('ШК ОТ/ВС водителя {0} поставлен на обновление.'.format(values['driver_number']))
                    logging.info('ШК ОТ/ВС водителя {0} поставлен на обновление.'.format(values['driver_number']))
                # event, values = window2.read()
                # window2.close()

        elif event == 'Стереть AUTH_USER_ID':
            print(delimiter)
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Водитель не найден.')
            else:
                db_request(auth_id_to_null.format(values['driver_number']))
                print('Стирание AUTH_USER_ID водителя {0} выполнено'.format(values['driver_number']))
                logging.info('Стирание AUTH_USER_ID водителя {0} выполнено'.format(values['driver_number']))

        elif event == 'Токен':
            # print(values['driver_number'])
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Некорректный табельный номер')
            else:

                try:
                    window.start_thread(lambda: api_driver_token(phone), '-driver_token-')
                    print(delimiter)
                    print('Запуск в фоновом режиме. Дождитесь выполнения операции.')
                except Exception as token_error:
                    print(token_error)

        elif event == '-driver_token-':
            settings['driver_token'] = values['-driver_token-']
            print(delimiter)
            print('Токен водителя {0}-{1} загружен'.format(values['driver_number'].strip(), phone))
            logging.info('Токен водителя {0}-{1} загружен'.format(values['driver_number'].strip(), phone))
            logging.info(settings['driver_token'])

        elif event == 'Сбросить пароль':
            # print(values['driver_number'])
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Некорректный табельный номер')
            else:
                window.start_thread(lambda: driver_pwd_reset(phone=phone), '-pwd_reset-')
                print(delimiter)
                print('Запуск в фоновом режиме. Дождитесь выполнения операции.')

        elif event == '-pwd_reset-':
            send_sms(phone)
            print(delimiter)
            print(f'Пароль водителя с телефоном {phone} сброшен. Смс о сбросе отправлено.')
            logging.info(f'Пароль водителя с телефоном {phone} сброшен. Смс о сбросе отправлено.')

        elif event == 'Версия':
            print(delimiter)
            phone = driver_phone(values['driver_number'].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                useragent = get_last_user_agent(values['driver_number'].strip())
                if not useragent:
                    print('Данные по версии не найдены')
                else:
                    print(useragent[0]['last_user_agent'])

        elif event == 'Закрыть инциденты':
            # print(values['driver_number'])
            phone = driver_phone(values['driver_number'])
            if not phone:
                print('Некорректный табельный номер')
            else:
                close_disp_inc(values['driver_number'])
                print(delimiter)
                print('Старые инциденты водителя {0} закрыты.'.format(values['driver_number']))
                logging.info('Старые инциденты водителя {0} закрыты.'.format(values['driver_number']))

        elif event == 'gpn_auth':
            window.start_thread(lambda: gpn_auth(), '-auth_done-')
            print(delimiter)
            print('Запуск в фоновом режиме. Дождитесь выполнения операции.')

        elif event == '-auth_done-':
            settings['gpn_session_id'] = values[event]
            print(delimiter)
            print('Сессия ГПН установлена')
            logging.info('Сессия ГПН установлена')
            logging.info(settings['gpn_session_id'])

        elif event == 'barcode':
            print(delimiter)
            if settings['driver_token'] and values['vtk'].strip():
                try:
                    response = get_vtk_barcode(values['vtk'].strip(), settings['driver_token'])
                    print(response)
                except Exception as error:
                    print(error)
            else:
                print('Токен не получен или отсутствует номер карты.')

        elif event == 'gpn_reset_counter':
            print(delimiter)
            if settings['gpn_session_id'] and values['vtk'].strip():
                print('Отправка запроса на сброс МПК карты {0}.'.format(values['vtk'].strip()))
                # print(values)
                try:
                    window.start_thread(lambda: gpn_reset_mpc(values['vtk'].strip(), settings['gpn_session_id']),
                                        '-gpn_reset_counter-')
                    print(delimiter)
                    print('Запуск в фоновом режиме. Дождитесь выполнения операции.')

                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты.')

        elif event == '-gpn_reset_counter-':
            print(values['-gpn_reset_counter-'])

        elif event == 'gpn_delete_mpc':
            print(delimiter)
            if settings['gpn_session_id'] and values['vtk'].strip():
                print('Отправка запроса на удаление карты {0}.'.format(values['vtk'].strip()))
                # print(values)
                try:
                    window.start_thread(lambda: gpn_delete_mpc(values['vtk'].strip(), settings['gpn_session_id']),
                                        '-gpn_delete_mpc-')
                    print(delimiter)
                    print('Запуск в фоновом режиме. Дождитесь выполнения операции.')
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты.')

        elif event == '-gpn_delete_mpc-':
            print(values['-gpn_delete_mpc-'])

        elif event == 'gpn_init_mpc':
            print(delimiter)
            if settings['gpn_session_id'] and values['vtk'].strip():
                print('Отправка запроса на выпуск карты {0}.'.format(values['vtk'].strip()))
                # print(values)
                try:
                    window.start_thread(lambda: gpn_init_mpc(values['vtk'].strip(), settings['gpn_session_id']),
                                        '-gpn_init_mpc-')
                    print(delimiter)
                    print('Запуск в фоновом режиме. Дождитесь выполнения операции.')
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты.')

        elif event == '-gpn_init_mpc-':
            print(values['-gpn_init_mpc-'])

        elif event == 'gpn_confirm_mpc':
            print(delimiter)
            if settings['gpn_session_id'] and values['vtk'].strip() and values['economist_code'].strip():
                print('Отправка кода экономиста.')
                # print(values)
                try:
                    window.start_thread(lambda: gpn_confirm_mpc(values['vtk'].strip(), values['economist_code'].strip(),
                                                                settings['gpn_session_id']), '-gpn_confirm_mpc-')
                    print(delimiter)
                    print('Запуск в фоновом режиме. Дождитесь выполнения операции.')
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введены номер карты\код экономиста.')

        elif event == '-gpn_confirm_mpc-':
            print(values['-gpn_confirm_mpc-'])

        elif event == 'Отправить СМС':
            print(delimiter)
            # print(values)
            if (values['sms_receiver'].strip().isdigit() and len(values['sms_receiver']) == 10 and
                    values['sms_body']):

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
