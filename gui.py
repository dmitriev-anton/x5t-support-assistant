# -*- coding: utf-8 -*-
import PySimpleGUI as SG
from driver import feature_dictionary
from vehicle import group_list
from pandas import DataFrame

f_dict = feature_dictionary()
g_list = group_list()


def main_window():
    """App gui"""
    # SG.set_options(font=("DejaVu Sans Mono", 10))
    SG.theme('DarkGreen5')

    vehicle_tab_layout = [
        [SG.Text('ТС'), SG.InputText(k='vehicle'), SG.Text('Группа'), SG.Combo(g_list, default_value=g_list[0], readonly=True, k='groups'),
         SG.Submit('Привязать')]
    ]

    invoice_tab_layout = [
        [SG.Text('Id_invoice'), SG.InputText(k='invoice_number'), SG.Submit('-->X5T ID')],
        [SG.Submit('Прожать'), SG.Submit('Отменить'), SG.Submit('Завершить'), SG.Submit('Чекпоинты'),
         SG.Submit('Бафнуть Х5Т')]
    ]

    drivers_tab_layout = [
        [SG.Text('Таб.н.'), SG.InputText(k='driver_number'), SG.Submit('Поиск'), SG.Submit('Рейсы'), SG.Submit('Путевые листы'),
         SG.Submit('ВТК'), SG.Submit('Токен'), SG.Submit('Сбросить пароль')],
        [SG.Submit('Фичи'), SG.Combo(f_dict, default_value=f_dict[0], readonly=True, k='feature'), SG.Submit('Добавить фичу'),
         SG.Submit('Удалить фичу'), SG.Submit('Деф. фичи', k='add_all'), SG.Submit('Удалить все', k='remove_all'),
         SG.Submit('ШК ОТ/ВС'), SG.Submit('Обновить ШК ОТ/ВС')]
    ]

    cards_tab_layout = [
        [SG.Text('Номер карты'), SG.InputText(size=(30, 3), key='vtk'), SG.Submit('Получить баркод',key='barcode'),
         SG.Text('Код экономиста'), SG.InputText(size=(8, 3), key='economist_code'),SG.Submit('ГПН.Сброс МПК',key='gpn_reset_counter')],
        [SG.Submit('ГПН.Авторизация', key='gpn_auth'), SG.Submit('ГПН.Удаление МПК',key='gpn_delete_mpc'),
         SG.Submit('ГПН.Выпуск МПК',key='gpn_init_mpc'), SG.Submit('ГПН.Код Экономиста',key='gpn_confirm_mpc')]
    ]

    sms_tab_layout = [
        [SG.Multiline(default_text='Введите текст сообщения', size=(80, 3), no_scrollbar=True, key='sms_body'),
         SG.InputText(default_text='Номер телефона', size=(15, 3), key='sms_receiver'),
         SG.Submit('Отправить СМС')]
    ]

    main_layout = [
        [SG.TabGroup([[SG.Tab('Привязка ТС', vehicle_tab_layout), SG.Tab('Рейс', invoice_tab_layout),
                       SG.Tab('Водители', drivers_tab_layout), SG.Tab('ВТК', cards_tab_layout),
                       SG.Tab('SMS', sms_tab_layout)]])],
        [SG.Output(size=(160, 25), font=("DejaVu Sans Mono", 9))]
    ]

    return SG.Window('X5T support assistant v2.16 by A.Dmitriev', main_layout, finalize=True)



def report_window(title: str, df: DataFrame):
    headings = df.columns.tolist()
    data = df.values.tolist()

    layout = [[SG.Table(values=data,
                        auto_size_columns=True,
                        headings=headings,
                        enable_events=True,
                        enable_click_events=True,
                        justification='left',
                        right_click_menu=['&Right', ['Copy']],
                        select_mode=SG.TABLE_SELECT_MODE_BROWSE,
                        expand_x=True,
                        expand_y=True,
                        key='-TABLE-'
                        )
               ]]

    return SG.Window(title, layout, finalize=True, resizable=True)
