# -*- coding: utf-8 -*-
from typing import List, Union

import PySimpleGUI as SG
from PySimpleGUI import TabGroup, Output

# from driver import feature_dictionary
# from vehicle import group_list
from vtk_api import tech_drivers_dict
from pandas import DataFrame

# f_dict = [i['id'] for  i in feature_dictionary()]
# g_list = group_list()
# s_list = ['NEW','FINISHED','DESTROYED']
# d_dict = tech_drivers_dict()

def main_window():
    """App gui"""
    # SG.set_options(font=("Segoe UI", 11))
    SG.theme('DarkGreen5')

    drivers_tab_layout = [
        [SG.Text('Таб.н.'),
         SG.InputText(k='driver_number'),
         SG.Submit('Поиск'),
         SG.Submit('ШК ОТ/ВС'),
         SG.Submit('Версия'),
         # SG.Submit('Токен'),
         # SG.Submit('Сбросить пароль')

         SG.Submit('Придумать пароль', key='generate_password')
         ],
        [
        SG.Submit('Рейсы'),
        SG.Submit('Путевые листы'),
        SG.Submit('ВТК'),
        # [SG.Submit('Все фичи'),
        #  SG.Submit('Фичи'),
        #  SG.Combo(f_dict, default_value=f_dict[0], readonly=True, k='feature'),
        #  SG.Submit('Добавить фичу'),
        #  SG.Submit('Удалить фичу'),
         # SG.Submit('Деф. фичи', k='add_all'),
         # SG.Submit('Удалить все', k='remove_all'),

         # SG.Submit('Обновить ШК ОТ/ВС'),
         # SG.Submit('Закрыть инциденты'),
         # SG.Submit('Стереть AUTH_USER_ID')]
            ]
    ]

    invoice_tab_layout = [
        [SG.Text('Id_invoice'),
         SG.InputText(k='invoice_number'),
         SG.Submit('-->X5T ID'),
         # SG.Text('Статус'),
         # SG.Combo(s_list, default_value=s_list[1], readonly=True, k='status', size=(13, 1)),
         # SG.Submit('Изменить')
         ],
        [SG.Submit('OWN_TRIP'),
         # SG.Submit('Точки'),
         SG.Submit('Прожатия'),
         # SG.Submit('Прожать'),
         # SG.Submit('Снять ожидание'),
         # SG.Submit('Снять АЗС')
         ]
    ]

    waybill_tab_layout = [
        [SG.Text('ПЛ'),
         SG.InputText(k='waybill_number'), SG.Submit('Поиск ПЛ'), SG.Submit('Рейсы на ПЛ'),
         SG.Submit('Осмотры')],
        [SG.Submit('Статус открытия'), SG.Submit('Лог открытия'), SG.Submit('Статус закрытия'),
         SG.Submit('Лог закрытия'),
         # SG.Submit('Закрыть ТРК ПЛ')
         ],
    ]

    # cards_tab_layout = [
    #     [SG.Text('Номер карты'),
    #      SG.InputText(size=(30, 3), key='vtk'),
    #      SG.Submit('Инфо', key='card_info'),
    #      SG.Submit('Получить баркод', key='barcode'),
    #      SG.Text('Код экономиста'),
    #      SG.InputText(size=(8, 3), key='economist_code'),
    #      SG.Text('Тех спец.'),
    #      SG.Combo(list(d_dict.keys()), readonly=True, k='tech_driver_name')],
    #     [SG.Submit('ГПН.Авторизация', key='gpn_auth'),
    #      SG.Submit('ГПН.ШК', key='gpn_barcode'),
    #      SG.Submit('ГПН.Сброс МПК', key='gpn_reset_counter'),
    #      SG.Submit('ГПН.Удаление МПК', key='gpn_delete_mpc'),
    #      SG.Submit('ГПН.Выпуск МПК', key='gpn_init_mpc'),
    #      SG.Submit('ГПН.Код Экономиста', key='gpn_confirm_mpc'),
    #      SG.Submit('ГПН.Отвязка карты', key='gpn_detach_card'),
    #      SG.Submit('ГПН.Привязка карты', key='gpn_attach_card'),
    #      ]
    # ]

    vehicle_tab_layout = [
        [SG.Text('ТС'),
         SG.InputText(k='vehicle'),
         SG.Submit('Искать ТС'),
         SG.Submit('Искать ПЛ'),
         # SG.Text('Группа'),
         # SG.Combo(g_list, default_value=g_list[0], readonly=True, k='groups'),
         # SG.Submit('Привязать')],
         SG.Submit('Топливные карты', key='show_cards'),
         SG.Submit('Подборы АЗС', key='show_finder_ops')
        ],
        [SG.Text('UUID'),
         SG.InputText(key='azs_ops'),
         SG.Submit('Статус Подбора АЗС', key='azs_finder_status')
         ]
        ]

    # sms_tab_layout = [
    #     [SG.Multiline(default_text='Введите текст сообщения', size=(80, 3), no_scrollbar=True, key='sms_body'),
    #      SG.InputText(default_text='Номер телефона', size=(15, 3), key='sms_receiver'),
    #      SG.Submit('Отправить СМС')]
    # ]

    main_layout = [
        [SG.TabGroup([[SG.Tab('Водители', drivers_tab_layout),
                       SG.Tab('Рейсы', invoice_tab_layout),
                       SG.Tab('ПЛ', waybill_tab_layout),
                       # SG.Tab('ВТК', cards_tab_layout),
                       SG.Tab('ТС', vehicle_tab_layout),
                       # SG.Tab('SMS', sms_tab_layout)
                       ]])],
        [SG.Output(size=(160, 25), font=("Consolas", 9),key='output_window')]
    ]

    return SG.Window('X5Transport support assistant 1Line v2.26 by A.Dmitriev',
                     main_layout,  return_keyboard_events=False, finalize=True)



# def report_window(title: str, df: DataFrame):
#     headings = df.columns.tolist()
#     data = df.values.tolist()
#
#     layout = [[SG.Table(values=data,
#                         auto_size_columns=True,
#                         headings=headings,
#                         enable_events=True,
#                         enable_click_events=True,
#                         justification='left',
#                         right_click_menu=['&Right', ['Copy']],
#                         select_mode=SG.TABLE_SELECT_MODE_BROWSE,
#                         expand_x=True,
#                         expand_y=True,
#                         key='-TABLE-'
#                         )
#                ]]
#
#     return SG.Window(title, layout, finalize=True, resizable=True)
