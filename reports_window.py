import PySimpleGUI as sg
from active_pl_races import all_races
from invoice import list_transform

def report_window(headers, data):
    table = sg.Table(values=data, headings=headers,
              auto_size_columns=True,
              display_row_numbers=False,
              justification='center', key='-TABLE-',
              selected_row_colors='black on yellow',
              enable_events=True,
              expand_x=True,
              expand_y=True,
              enable_click_events=True)

    layout = [[table]]
    return sg.Window('Вывод', layout)

def main():
    tab_num = '01251548'
    result = all_races(tab_num)
    data =[]
    data = list_transform(result)
    print(data[0])
    print(data[1:])
    window = report_window(data[0], data[1:])
    while True:
        event, values = window.read()
        print("event:", event, "values:", values)
        if event == sg.WIN_CLOSED:
            break
        if '+CLICKED+' in event:
            sg.popup("You clicked row:{} Column: {}".format(event[2][0], event[2][1]))
    window.close()

if __name__ == '__main__':
    main()
