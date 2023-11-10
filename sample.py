import PySimpleGUI as psg
def win1():
   layout = [
      [psg.Text('This is the FIRST WINDOW'), psg.Text('', key='-OUTPUT-')],
      [psg.Text('popup one')],
      [psg.Button('Window-2'), psg.Button('Popup'), psg.Button('Exit')]
   ]
   return psg.Window('Window Title', layout, finalize=True)
def win2():
      layout = [[psg.Text('The second window')],[psg.Input(key='-IN-', enable_events=True)],
                [psg.Text(size=(25, 1), key='-OUTPUT-')],
                [psg.Button('Erase'), psg.popup('Popup two'), psg.Button('Exit')]]
      return psg.Window('Second Window', layout, finalize=True)
window1 = win1()
window2 = None
while True:
   window, event, values = psg.read_all_windows()
   print(window.Title, event, values)
   if event == psg.WIN_CLOSED or event == 'Exit':
      window.close()
   #if window == window2:
 #       window2 = None
#   elif window == window1:
 #     break
   if event == 'Popup':
      psg.popup('Hello Popup')
   elif event == 'Window-2' and not window2:
        #window2 = win2()
#   elif event == '-IN-':
#      window['-OUTPUT-'].update('You entered {}'.format(values["-IN-"]))
#   elif event == 'Erase':
 #     window['-OUTPUT-'].update('')
  #    window['-IN-'].update('')
#window.close()