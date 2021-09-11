import PySimpleGUI as sg
from client import Client

sg.theme('Black')

layout_startup = [
    [sg.Text("Remote Host")],
    [sg.Input(key='host')],
    [sg.Text("Remote Port")],
    [sg.Input(key='port')],
    [sg.Text("Nickname")],
    [sg.Input(key='nickname')],
    [sg.Button(button_text="Connect", bind_return_key=True), sg.Button(button_text="Exit")]
]

chat_active = False
window_startup = sg.Window("Connect to a Server", layout=layout_startup)
while True:
    event_startup, values_startup = window_startup.read()
    if event_startup == sg.WIN_CLOSED or event_startup == 'Exit':
        break
    if event_startup == 'Connect':
        window_startup.hide()
        chat_active = True
        layout_chat = [
            [sg.Multiline(key='output', size=(80, 30), autoscroll=True, disabled=True, reroute_stdout=True, auto_refresh=True)],
            [sg.Input(key='input', size=(80, 1), enable_events=True, focus=True)],
            [sg.Button(button_text="Send", bind_return_key=True), sg.Button(button_text="Leave")]
        ]
        window_chat = sg.Window(f"PyChat - {values_startup['host']}:{values_startup['port']}", layout=layout_chat, finalize=True)
        try:
            client = Client(values_startup['host'], int(values_startup['port']), values_startup['nickname'])
            client.start()
            while True:
                event_chat, values_chat = window_chat.read()
                if event_chat == sg.WIN_CLOSED or event_chat == 'Leave':
                    break
                if event_chat == 'Send':
                    client.send(values_chat['input'])
                    window_chat['input'].update(value='')
        except Exception as exception:
            print(f"Exception: {exception}")
        finally:
            client.stop()
            window_chat.close()
            chat_active = False
            window_startup.un_hide()
window_startup.close()
