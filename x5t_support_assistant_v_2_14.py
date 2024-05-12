# -*- coding: utf-8 -*-
import logging
import warnings

from pandas import DataFrame
from tabulate import tabulate
import PySimpleGUI as SG
from bee_sms import send_sms
from driver import *
from driver_api import driver_pwd_reset
from vtk_api import *
from invoice import Invoice, finish, checkpoints, checkpoints_aio, get_x5t_id
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

    m_window, report = main_window(), None  # вызов главного окна

    settings = {
        'driver-token': '',
        'gpn_session_id': '',
    }

    while True:  # The Event Loop

        # window, event, values = SG.read_all_windows()
        # event, values = m_window.read()
        # vehicle_code = group = None

        window, event, values = SG.read_all_windows()
        if event == SG.WIN_CLOSED or event == 'Exit':
            window.close()
            if window == report:  # if closing win 2, mark as closed
                window2 = None
            elif window == m_window:  # if closing win 1, exit program
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

                if not values[1]:
                    db_request(car_drop.format(vehicle_code))
                    print(f'ТС {vehicle_code} отвязана.')
                    logging.info(f'ТС {vehicle_code} отвязана.')

                else:
                    db_request(car_assign.format(values[1], vehicle_code))
                    print(f'ТС {vehicle_code} привязана к группе {values[1]}.')
                    logging.info(f'ТС {vehicle_code} привязана к группе {values[1]}.')

        if event == '-->X5T ID':
            # print('------------------------------------------------------------------------------------')
            # x5tid = None
            if not values[2].strip():
                print('------------------------------------------------------------------------------------')
                print('Неверный номер!!!')
                # print(values)
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
            # print('Функционал отключен.')
            tasks()
            logging.info('Запуск бафера')

        if event == 'Чекпоинты':
            print('--------------------------------------------------------------------------------------')
            if not values[2]:
                print('Введите номер рейса х5т')
            else:
                points = checkpoints(values[2])
                if points:
                    points = DataFrame(points)
                    print(tabulate(points, headers='keys', tablefmt='tsv'))
                else:
                    print('Прожатия отсутствуют!')

        if event == 'Поиск':
            print('------------------------------------------------------------------------------------')
            # print(values)
            if not values[3].strip():
                print('Введите данные для поиска.')
            else:
                drv = search_driver(values[3].strip())
                if not drv:
                    print('Водитель не найден')
                else:
                    if len(drv) == 1:
                        # если найден только 1 водитель подставлять табельный с нулями
                        # print(drv[0]['number'])
                        m_window[3].update(drv[0]['number'])

                    drv = DataFrame(drv)
                    # report = report_window('Поиск водителей', drv) # запускает новое окно табличного отчета
                    print(tabulate(drv, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))

        if event == 'Путевые листы':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                waybills = driver_waybills(values[3].strip())
                if not waybills:
                    print('Путевые листы со статусом в работе отсутствуют.')
                else:
                    waybills = DataFrame(waybills)
                    print(tabulate(waybills, headers='keys', showindex=False, tablefmt='tsv', numalign='left'))

        if event == 'ВТК':
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
                    print(error)

        if event == 'Рейсы':
            # races = []
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3].strip())
            if not phone:
                print('Водитель не найден.')
            else:
                races = all_races(values[3].strip())

                if races:
                    races = DataFrame(races)
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
                if not features:
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
                if not features:
                    print('У водителя дефолтный набор фич')

                elif values[4] not in f_dict:
                    print('Внимание!Некорректная фича!')

                else:
                    res = add_feature(values[3], values[4])
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
                if not features:
                    print('У водителя дефолтный набор фич')

                elif values[4] not in f_dict:
                    print('Внимание!Некорректная фича!')

                else:
                    res = remove_feature(values[3], values[4])
                    print(res)
                    logging.info(res)

        if event == 'ШК ОТ/ВС':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3])
            if not phone:
                print('Водитель не найден.')
            else:
                ot_id = db_request(ot_check.format(values[3]))
                if not ot_id:
                    print('ШК ОТ/ВС отсутствует')
                else:
                    print(ot_id[0])
                    # print(tabulate(ot_id, headers='keys', tablefmt='tsv'))

        if event == 'Обновить ШК ОТ/ВС':
            print('------------------------------------------------------------------------------------')
            phone = driver_phone(values[3])
            if not phone:
                print('Водитель не найден.')
            else:
                ot_id = db_request(ot_check.format(values[3]))
                if not ot_id:
                    db_request(ot_insrt.format(values[3]))
                    print(f'ШК ОТ/ВС водителя {values[3]} прописан и поставлен на обновление.')
                    logging.info(f'ШК ОТ/ВС водителя {values[3]} прописан и поставлен на обновление.')
                else:
                    db_request(ot_upd.format(values[3]))
                    print(f'ШК ОТ/ВС водителя {values[3]} поставлен на обновление.')
                    logging.info(f'ШК ОТ/ВС водителя {values[3]} поставлен на обновление.')
                # event, values = window2.read()
                # window2.close()

        if event == 'Токен':
            print('------------------------------------------------------------------------------------')
            # print(values[3])
            phone = driver_phone(values[3].strip())
            if not phone:
                print('Некорректный табельный номер')
            else:
                try:
                    settings['driver_token'] = api_driver_token(phone)
                    print(f'Токен водителя {values[3].strip()}-{phone} загружен')
                    print(settings['driver_token'])
                except Exception as token_error:
                    print(token_error)

        if event == 'Сбросить пароль':
            print('------------------------------------------------------------------------------------')
            # print(values[3])
            phone = driver_phone(values[3])
            if not phone:
                print('Некорректный табельный номер')
            else:
                rst_result = driver_pwd_reset(phone=phone)
                if rst_result:
                    send_sms(phone)
                    print(f'Пароль водителя с телефоном {phone} сброшен. Смс о сбросе отправлено.')
                    logging.info(f'Пароль водителя с телефоном {phone} сброшен. Смс о сбросе отправлено.')
                else:
                    print(rst_result)

        if event == 'ГПН.Авторизация':
            print('------------------------------------------------------------------------------------')
            settings['gpn_session_id'] = gpn_auth()
            print('ГПН сессия установлена.')

        if event == 'ГПН.Удаление МПК':
            print('------------------------------------------------------------------------------------')
            if settings['gpn_session_id'] and values[4].strip():
                try:
                    response = gpn_delete_mpc(values[4].strip(), settings['gpn_session_id'])
                    print(response)
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты.')

        if event == 'ГПН.Выпуск МПК':
            print('------------------------------------------------------------------------------------')
            if settings['gpn_session_id'] and values[4].strip():
                try:
                    response = gpn_init_mpc(values[4].strip(), settings['gpn_session_id'])
                    print(response)
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введен номер карты.')

        if event == 'ГПН.КОД Экономиста':
            print('------------------------------------------------------------------------------------')
            if settings['gpn_session_id'] and values[4].strip() and values[5].strip():
                try:
                    response = gpn_confirm_mpc(values[4].strip(), values[5].strip(), settings['gpn_session_id'])
                    print(response)
                except Exception as error:
                    print(error)
            else:
                print('Сессия не установлена или не введены номер карты\код экономиста.')

        if event == 'Отправить СМС':
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
