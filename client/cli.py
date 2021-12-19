import string
from sys import stdout
from threading import Thread, Event
from pyco import terminal, cursor, print_message
from pyco.utils import kbhit, getch
from commands import Commands


class UI(Thread):
    def __init__(self, name: str = 'UIThread', daemon: bool = False, prefix: str = '> ', padding_lines: int = 3):
        self._name = name
        self._daemon = daemon
        self.padding_lines = padding_lines
        self.prefix = prefix
        self.input_line = terminal.get_size().lines
        self.output_line = cursor.get_position()[0]
        self.stop_event = Event()
        self.allow_output = Event()
        self.allow_output.set()
        self.data = ''
        self.commands = Commands(self)

    def start(self):
        cursor.set_position(0, self.input_line)
        terminal.clear_line()
        if self.input_line - self.output_line < self.padding_lines:
            terminal.scroll_up(1)
            self.output_line -= 1
        stdout.write(self.prefix + self.data)
        stdout.flush()
        self.stop_event.clear()
        self.allow_output.set()
        self.input_thread = Thread(target=self.input, name=self._name, daemon=self._daemon)
        self.input_thread.start()

    def stop(self):
        self.stop_event.set()

    def input(self):
        while not self.stop_event.is_set():
            if kbhit():
                self.allow_output.clear()
                key = getch()
                if key in ['\000', '\x00', '\xe0']:
                    key += getch()
                if key in string.printable:
                    self.data += key
                    stdout.write(key)
                    stdout.flush()
                if key == '\x08':
                    if self.data:
                        self.data = self.data[:-1]
                        stdout.write('\x08 \x08')
                        stdout.flush()
                if key == '\r':
                    cursor.set_position(0, self.input_line)
                    terminal.clear_line()
                    stdout.write(self.prefix)
                    stdout.flush()
                    self.allow_output.set()
                    data = self.data
                    self.data = ''
                    self.commands.input(data)
                self.allow_output.set()

    def output(self, data: str):
        self.allow_output.wait()
        self.stop()
        cursor.set_position(0, self.output_line)
        terminal.clear_line()
        print_message(data)
        self.output_line += 1
        self.start()


if __name__ == '__main__':
    ui = UI()
    ui.start()
