import PySimpleGUI as sg
from driver import all_races
from pandas import DataFrame

def report_window(headers, data):
    table = sg.Table(values=data, headings=headers,
              auto_size_columns=True,
              display_row_numbers=False,
              justification='center', key='-TABLE-',
              selected_row_colors='black on yellow',
              enable_events=True,
              expand_y=True,
              enable_click_events=True)

    layout = [[table]]
    return sg.Window('Вывод', layout)

def main():
    tab_num = '00642700'
    data = DataFrame(all_races(tab_num))
    print(data.values)
    window = report_window(data=data, headers=list(data.keys()))
    event, value = window.read()


if __name__ == '__main__':
    main()
