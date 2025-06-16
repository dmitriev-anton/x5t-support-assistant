# -*- coding: utf-8 -*-
import logging
import warnings
import tkinter as tk
import PySimpleGUI as SG
from pandas import DataFrame
from tabulate import tabulate
import random
from driver import *
from driver_api import *
# from x5t_tasks import tasks ----- unused
from gui import main_window, d_dict
from invoice import *
from megafon_sms import megafon_send_sms
from vehicle import *
from vtk_api import *
from waybill import *
from x5t_connect import db_request




def main():
    def get_active_element_key(window):
        """Возвращает ключ элемента с фокусом или None"""
        focused_widget = window.TKroot.focus_get()
        for key in window.key_dict:
            element = window[key]
            if hasattr(element, 'Widget') and element.Widget == focused_widget:
                return key
        return None
    def handle_ctrl_key(event):
        # Проверяем, что нажат Ctrl (бит 0x0004 в event.state)
        if event.state & 0x0004:
            # print(get_active_element_key(window))
            # Обработка Ctrl+C (код клавиши 'C' = 67)
            if event.keycode == 67:
                widget = window[get_active_element_key(window)].Widget
                try:
                    # Получаем выделенный текст
                    selected_text = widget.selection_get()
                    # print(selected_text)
                    SG.clipboard_set(selected_text)  # Копируем в буфер
                except:
                    pass
                return 'break'  # Блокируем стандартное поведение

            # Обработка Ctrl+V (код клавиши 'V' = 86)
            elif event.keycode == 86:
                # print(get_active_element_key(window))
                try:
                    widget = window[get_active_element_key(window)].Widget
                    text_to_paste = SG.clipboard_get()  # Получаем текст из буфера
                    # print(text_to_paste)
                    # widget.insert(tk.INSERT, text_to_paste)  # Вставляем
                    # window[get_active_element_key(window)].update(text_to_paste)
                except:
                    pass
                return 'break'  # Блокируем стандартное поведение

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
    window.TKroot.bind('<Control-KeyPress>', handle_ctrl_key)

    delimiter = '-' * 160  # разделитель для вывода
    settings = {  # хранение токенов для запросов
        'driver_token': '',
        'gpn_session_id': '',
    }
    tablefmt = "plain"  # 'simple', 'tsv' - подходят

    while True:  # The Event Loop

        event, values = window.read()

        # print(f'Событие: {event}')
        # print(f'значение: {values}')


        if event in (SG.WIN_CLOSED, 'Exit'):
            break

        # elif event.find('??') != -1:
        #     print(event)

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

        elif event == 'Искать ТС':
            print(delimiter)
            vehicle_code = car_num_to_latin(values['vehicle'].strip())

            if not vehicle_code:
                print('Отсутствует номер ТС.')

            else:
                window['vehicle'].update(vehicle_code)
                vehicle = search_vehicle(vehicle_code)

                if len(vehicle) == 1:
                    window['vehicle'].update(vehicle[0]['code'])

                if vehicle:
                    print(tabulate(DataFrame(vehicle), headers='keys', showindex=False,tablefmt=tablefmt))

                else:
                    print('ТС не найдены')

        elif event == 'Искать ПЛ':
            print(delimiter)
            vehicle_code = car_num_to_latin(values['vehicle'].strip())
            window['vehicle'].update(vehicle_code)
            wbs = search_wb_by_vehicle(vehicle_code)

            if not vehicle_code:
                print('Отсутствует номер ТС.')

            elif vehicle_counter(vehicle_code) == 0:
                print(f'ТС {vehicle_code} в системе х5транспорт отсутствует. Укажите существующий номер.')

            else:
                # print(wbs)
                if wbs:
                    print(tabulate(DataFrame(wbs), headers='keys', showindex=False,tablefmt=tablefmt))
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
                    print(tabulate(DataFrame(x5tids), headers='keys', showindex=False, tablefmt=tablefmt))

                else:
                    print('Номер не найден!')

        elif event == 'OWN_TRIP':
            if not values['invoice_number'].strip():
                print(delimiter)
                print('Введите номер рейса х5т')
            else:
                ots = get_own_trip(values['invoice_number'].strip())
                print(delimiter)
                if ots:
                    print(tabulate(DataFrame(ots), headers='keys', tablefmt=tablefmt))
                else:
                    print('Записи отсутствуют')

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

        elif event == 'Снять ожидание':
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
                window.start_thread(lambda: cure_invoice(values['invoice_number'].strip()), '-cure_invoice-')
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
        # unused functional
        # elif event == 'Бафнуть Х5Т':
        #     # print('Функционал отключен.')
        #     window.perform_long_operation(tasks, '-tasks-')
        #     print(delimiter)
        #     print('Запуск бафера')
        #     logging.info('Запуск бафера')

        # elif event == '-tasks-':
        #     print(delimiter)
        #     print('Фиксы применены')

        elif event == 'Прожатия':
            print(delimiter)
            if not values['invoice_number']:
                print('Введите номер рейса х5т')
            else:
                points = checkpoints(values['invoice_number'])
                if points:
                    print(tabulate(DataFrame(points), headers='keys', showindex=False, tablefmt=tablefmt))
                else:
                    print('Прожатия отсутствуют!')

        elif event == 'Точки':
            print(delimiter)
            if not values['invoice_number']:
                print('Введите номер рейса х5т')
            else:
                stages = invoice_unloading_points(values['invoice_number'])
                if stages:
                    print(tabulate(DataFrame(stages), headers='keys', showindex=False, tablefmt=tablefmt))
                else:
                    print('Некорректный номер рейса!')

        elif event == 'Поиск ПЛ':
            print(delimiter)
            if not values['waybill_number'].strip():
                print('Введите данные для поиска.')
            else:
                wb = search_waybill(values['waybill_number'].strip())
                if not wb:
                    print('Путевые листы не найдены')
                else:
                    print(tabulate(DataFrame(wb), headers='keys', showindex=False, tablefmt=tablefmt,
                                   numalign='left'))

        elif event == 'Статус открытия':
            print(delimiter)
            log = []
            if not values['waybill_number'].strip():
                print('Введите данные для поиска.')
            else:
                log = wb_open_status(values['waybill_number'].strip())
                if not log:
                    print('Записи отсутствуют')
                else:
                    print(tabulate(DataFrame(log), headers='keys', showindex=False, tablefmt=tablefmt,
                                   numalign='left'))
        elif event == 'Лог открытия':
            print(delimiter)
            log = []
            if not values['waybill_number'].strip():
                print('Введите данные для поиска.')
            else:
                log = wb_open_log(values['waybill_number'].strip())
                if not log:
                    print('Записи отсутствуют')
                else:
                    print(tabulate(DataFrame(log), headers='keys', showindex=False, tablefmt=tablefmt,
                                   numalign='left'))

        elif event == 'Статус закрытия':
            print(delimiter)
            log = []
            if not values['waybill_number'].strip():
                print('Введите данные для поиска.')
            else:
                log = wb_close_status(values['waybill_number'].strip())
                if not log:
                    print('Записи отсутствуют')
                else:
                    print(tabulate(DataFrame(log), headers='keys', showindex=False, tablefmt=tablefmt,
                                   numalign='left'))

        elif event == 'Лог закрытия':
            print(delimiter)
            log = []
            if not values['waybill_number'].strip():
                print('Введите данные для поиска.')
            else:
                log = wb_close_log(values['waybill_number'].strip())
                if not log:
                    print('Записи отсутствуют')
                else:
                    print(tabulate(DataFrame(log), headers='keys', showindex=False, tablefmt=tablefmt,
                                   numalign='left'))

        elif event == 'Рейсы на ПЛ':
            print(delimiter)
            if not values['waybill_number'].strip():
                print('Введите данные для поиска.')
            else:
                races = search_invoices_on_wb(values['waybill_number'].strip())
                if not races:
                    print('На ПЛ {} рейсы отсутствуют.'.format(values['waybill_number'].strip()))
                else:
                    print(tabulate(DataFrame(races), headers='keys', showindex=False, tablefmt=tablefmt,
                                   numalign='left'))

        elif event == 'Осмотры':
            print(delimiter)
            briefing = []
            if not values['waybill_number'].strip():
                print('Введите данные для поиска.')
            else:
                briefing = briefing_report(values['waybill_number'].strip())
                if not briefing:
                    print('Записи отсутствуют')
                else:
                    print(tabulate(DataFrame(briefing), headers='keys', showindex=False, tablefmt=tablefmt,
                                   numalign='left'))

        elif event == 'Закрыть ТРК ПЛ':
            print(delimiter)
            if not values['waybill_number'].strip():
                print('Введите данные для поиска.')
            elif not values['waybill_number'].strip().startswith('TRC'):
                print('ПЛ не ТРК. Введите корректный номер.')
            else:
                close_wb(values['waybill_number'].strip())
                print('ПЛ {} закрыт.'.format(values['waybill_number'].strip()))
                logging.info('ПЛ {} закрыт.'.format(values['waybill_number'].strip()))

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
                    print(tabulate(DataFrame(cards), headers='keys', showindex=False, tablefmt=tablefmt, numalign='left'))
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

        elif event == 'Все фичи':
            print(delimiter)
            print(tabulate(DataFrame(feature_dictionary()), headers='keys', showindex=False, tablefmt=tablefmt))

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
                    print(tabulate(DataFrame(features), headers='keys', showindex=False, tablefmt=tablefmt))

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

        # elif event == 'add_all':
        #     print(delimiter)
        #     phone = driver_phone(values['driver_number'])
        #     if not phone:
        #         print('Водитель не найден.')
        #     else:
        #         f4s = driver_features(values['driver_number'].strip())
        #         if not f4s:
        #             res = add_feature(values['driver_number'].strip(), default_features_set())
        #             print(res)
        #             logging.info(res)
        #         else:
        #             print('Добавление невозможно.У водителя уже присутствуют фичи.')
        #
        # elif event == 'remove_all':
        #     print(delimiter)
        #     phone = driver_phone(values['driver_number'].strip())
        #     if not phone:
        #         print('Водитель не найден.')
        #     else:
        #         # res = []
        #         features = driver_features(values['driver_number'])
        #         if features:
        #             res = remove_feature(values['driver_number'].strip())
        #             print(res)
        #             logging.info(res)
        #         else:
        #             print('Удаление невозможно.У водителя отсутствуют фичи.')

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

        # elif event == 'Токен':
        #     # print(values['driver_number'])
        #     settings['phone'] = driver_phone(values['driver_number'].strip())
        #     if not settings['phone']:
        #         print('Некорректный табельный номер')
        #     else:
        #
        #         try:
        #             print(delimiter)
        #             window.start_thread(lambda: api_driver_token(settings['phone'], settings['phone'][4:]), '-driver_token-')
        #             print('Запуск в фоновом режиме. Дождитесь выполнения операции.')
        #         except Exception as token_error:
        #             print(delimiter)
        #             print(token_error)

        elif event == '-driver_token-':
            settings['driver_token'] = values['-driver_token-']
            print(delimiter)
            print('Токен водителя {0} загружен'.format(values['driver_number'].strip()))
            logging.info('Токен водителя {0} загружен'.format(values['driver_number'].strip()))
            logging.info(settings['driver_token'])
            settings['phone'] = None

        elif event == 'Сбросить пароль':
            print(delimiter)
            # print(values['driver_number'])
            settings['phone'] = driver_phone(values['driver_number'].strip())
            if not settings['phone']:
                print('Некорректный табельный номер')
            else:
                password = generate_password()
                window.start_thread(lambda: driver_pwd_reset(settings['phone'], password), '-pwd_reset-')
                print('Запуск в фоновом режиме. Дождитесь выполнения операции.')

        elif event == '-pwd_reset-':
            megafon_send_sms(phone=settings['phone'], password=password)
            if not settings['driver_token']:
                window.start_thread(lambda: api_driver_token(phone=settings['phone'], password=password), '-driver_token-')
            print(delimiter)
            print('Пароль водителя с телефоном {0} сброшен на {1} Смс о сбросе отправлено.'.format(settings['phone'], password))
            logging.info('Пароль водителя с телефоном {0} сброшен на {1} Смс о сбросе отправлено.'.format(settings['phone'], password))
            settings['phone'] = None

        elif event == 'Версия':
            print(delimiter)
            settings['phone'] = driver_phone(values['driver_number'].strip())
            if not settings['phone']:
                print('Водитель не найден.')
            else:
                useragent = get_last_user_agent(values['driver_number'].strip())
                if not useragent:
                    print('Данные по версии не найдены')
                else:
                    print(useragent[0]['last_user_agent'])
                    settings['phone'] = None

        # elif event == 'Закрыть инциденты':
        #     # print(values['driver_number'])
        #     settings['phone'] = driver_phone(values['driver_number'])
        #     if not settings['phone']:
        #         print('Некорректный табельный номер')
        #     else:
        #         close_disp_inc(values['driver_number'].strip())
        #         print(delimiter)
        #         print('Старые инциденты водителя {0} закрыты.'.format(values['driver_number']))
        #         logging.info('Старые инциденты водителя {0} закрыты.'.format(values['driver_number']))
        #         settings['phone'] = None

        elif event == 'gpn_auth':
            window.start_thread(lambda: gpn_auth(), '-auth_done-')
            print(delimiter)
            print('Запуск в фоновом режиме. Дождитесь выполнения операции.')

        elif event =='gpn_barcode':
            print(delimiter)
            # print(settings['gpn_session_id'], values['vtk'].strip(), get_vtk_info(values['vtk'].strip()))
            if (settings['gpn_session_id'] and values['vtk'].strip()
                    and get_vtk_info(values['vtk'].strip())['azs_company_id'] == 1002):
                print('Запрос ШК карты {0}.'.format(values['vtk'].strip()))
                # print(values)
                try:
                    window.start_thread(lambda: gpn_barcode_check(values['vtk'].strip(), settings['gpn_session_id']),
                                        '-gpn_barcode-')
                    print(delimiter)
                    print('Запуск в фоновом режиме. Дождитесь выполнения операции.')

                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты или карта не ГПН')

        elif event == '-gpn_barcode-':
            print(delimiter)
            print(values['-gpn_barcode-'])


        elif event == '-auth_done-':
            if values[event]['status']['code'] == 200:
                settings['gpn_session_id'] = values[event]['data']['session_id']
                print(delimiter)
                print('Сессия ГПН установлена.')
                logging.info('Сессия ГПН установлена')
                logging.info(settings['gpn_session_id'])
            else:
                print(delimiter)
                print('Сессия ГПН не установлена. Повторный запуск.')
                window.start_thread(lambda: gpn_auth(), '-auth_done-')
                print(delimiter)
                print('Запуск в фоновом режиме. Дождитесь выполнения операции.')

        elif event == 'card_info':
            print(delimiter)
            if values['vtk'].strip():
                try:
                    settings['card_details'] = get_vtk_info(values['vtk'].strip())

                except Exception as error:
                    print(error)

            if settings['card_details']:
                # print(settings['card_details'])
                print(tabulate(DataFrame([settings['card_details']]), headers='keys', showindex=False, tablefmt=tablefmt))
            else:
                print('Карта не найдена')

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
            print(delimiter)
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
            print(delimiter)
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
            print(delimiter)
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
            print(delimiter)
            print(values['-gpn_confirm_mpc-'])

        elif event == 'gpn_detach_card':
            print(delimiter)
            if settings['gpn_session_id'] and values['vtk'].strip() and values['tech_driver_name']:
                # print(values)
                try:
                    window.start_thread(lambda: detach_card(values['vtk'].strip(), d_dict[values['tech_driver_name']],
                                                                settings['gpn_session_id']), '-gpn_detach_card-')
                    print('Запуск в фоновом режиме. Дождитесь выполнения операции.')
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введены номер карты\код экономиста.')

        elif event == '-gpn_detach_card-':
            print(delimiter)
            print(values['-gpn_detach_card-'])

        elif event == 'gpn_attach_card':
            print(delimiter)
            if settings['gpn_session_id'] and values['vtk'].strip() and values['tech_driver_name']:
                # print(values)
                try:
                    window.start_thread(lambda: attach_card(values['vtk'].strip(), d_dict[values['tech_driver_name']],
                                                                settings['gpn_session_id']), '-gpn_attach_card-')
                    print('Запуск в фоновом режиме. Дождитесь выполнения операции.')
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введены номер карты\код экономиста.')

        elif event == '-gpn_attach_card-':
            print(delimiter)
            print(values['-gpn_attach_card-'])

        elif event == 'Отправить СМС':
            print(delimiter)
            # print(values)
            if (values['sms_receiver'].strip().isdigit() and len(values['sms_receiver']) == 10 and
                    values['sms_body']):

                try:
                    megafon_send_sms(values['sms_receiver'].strip(), values['sms_body'].replace("\n", " "))
                    print('СМС отправлено на номер {0}'.format(values['sms_receiver'].strip()))
                    logging.info('СМС отправлено на номер {0}'.format(values['sms_receiver'].strip()))
                except Exception as error:
                    print(error)
            else:
                print('Некорректные данные! Перепроверьте правильность ввода!')


if __name__ == "__main__":
    main()
