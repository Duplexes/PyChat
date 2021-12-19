import PySimpleGUI as sg
from commands import Commands


class UI:
    def __init__(self):
        sg.theme('Black')
        self.layout_startup = [
            [sg.Text("Remote Host")],
            [sg.Input(key='host')],
            [sg.Text("Remote Port")],
            [sg.Input(key='port')],
            [sg.Text("Nickname")],
            [sg.Input(key='nickname')],
            [sg.Button(button_text="Connect", bind_return_key=True), sg.Button(button_text="Exit")]
        ]
        self.chat_active = False
        self.stop_event = False
        self.exit_event = False
        self.commands = Commands(self)

    def start(self):
        self.stop_event = False
        self.window_startup = sg.Window("Connect to a Server", layout=self.layout_startup)
        while not self.exit_event:
            self.event_startup, self.values_startup = self.window_startup.read(1000)
            if self.event_startup == sg.WIN_CLOSED or self.event_startup == 'Exit':
                break
            if self.event_startup == 'Connect':
                self.window_startup.hide()
                self.chat_active = True
                layout_chat = [
                    [sg.Multiline(key='output', size=(80, 30), autoscroll=True, disabled=True, auto_refresh=True)],
                    [sg.Input(key='input', size=(80, 1), enable_events=True, focus=True)],
                    [sg.Button(button_text="Send", bind_return_key=True), sg.Button(button_text="Leave")]
                ]
                self.window_chat = sg.Window(f"PyChat - {self.values_startup['host']}:{self.values_startup['port']}", layout=layout_chat, finalize=True)
                try:
                    self.commands.join(self.values_startup['host'], int(self.values_startup['port']), self.values_startup['nickname'])
                    while not self.stop_event:
                        self.event_chat, self.values_chat = self.window_chat.read(1000)
                        if self.event_chat == sg.WIN_CLOSED or self.event_chat == 'Leave':
                            break
                        if self.event_chat == 'Send':
                            self.input(self.values_chat['input'])
                except Exception as exception:
                    print(f"Exception: {exception}")
                finally:
                    self.commands.exit()
                    self.window_chat.close()
                    self.chat_active = False
                    self.window_startup.un_hide()
        self.commands.exit()
        self.window_startup.close()

    def stop(self):
        self.stop_event = True

    def exit(self):
        self.stop_event = True
        self.exit_event = True

    def input(self, value: str):
        self.commands.input(value)
        self.window_chat['input'].update(value='')

    def output(self, value: str):
        print(value)
        # self.window_chat['output'].update(str(value) + '\n', append=True)


if __name__ == '__main__':
    ui = UI()
    ui.start()
