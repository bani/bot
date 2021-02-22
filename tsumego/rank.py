import PySimpleGUI as sg
import threading
import time


W = 30 # string width

def open_window():
    while True:
        event, value = window.read()
        if event == sg.WIN_CLOSED:
            break

    window.close()

def update(players, last):
    i = 1
    for p in sorted(players.items(), key=lambda x: -x[1]):
        window[i].update(f"{i}. {p[0]}".ljust(W))
        i+=1
        if i > 5:
            break
    if last:
        window[0].update(f"{last}".ljust(W))
    window.refresh()

sg.theme('DarkPurple')   # Add a touch of color
font = {'font': 'Courier 20 bold', 'text_color': 'white'}
font2 = {'font': 'Sans-Serif 20', 'text_color': 'white'}
# All the stuff inside your window.
layout = [  
            [sg.Text(''.ljust(W), key=1, **font)],
            [sg.Text(''.ljust(W), key=2, **font)],
            [sg.Text(''.ljust(W), key=3, **font)],
            [sg.Text(''.ljust(W), key=4, **font)],
            [sg.Text(''.ljust(W), key=5, **font)],
            [sg.Text(''.ljust(W), **font)],
            [sg.Text('Last correct answer:'.ljust(W), **font2)],
            [sg.Text(''.ljust(W), key=0, **font2)], ]

# Create the Window
window = sg.Window('Top Players', layout)

t = threading.Thread(target=open_window)
t.start()
time.sleep(1)

