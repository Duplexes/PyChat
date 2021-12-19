import socket
from threading import Thread, Event


class Client:
    def __init__(self, commands, sock: socket.socket = None):
        try:
            from commands import Commands
            self.commands: Commands = commands
        except ImportError:
            self.commands = commands
        try:
            self.sock = sock if sock is not None else socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0, None)
            self.stop_event = Event()
            self.idle_thread = Thread(target=self._idle, daemon=False, name='IdleThread')
            self.idle_thread.start()
            self.receive_thread = Thread(target=self.receive, daemon=True, name='ReceiveThread')
            self.sock.settimeout(5)
            self.commands.output("Client initialized")
        except Exception as exception:
            self.commands.output(exception)

    def _idle(self):
        while not self.stop_event.is_set():
            pass

    def join(self, host: str, port: int, name: str):
        try:
            self.host = host
            self.port = int(port)
            self.name = name
            self.sock.connect((self.host, self.port))
            print(self.sock)
            self.receive_thread.start()
        except Exception as exception:
            self.commands.output(exception)
            self.exit()

    def exit(self):
        self.stop_event.set()
        self.sock.close()

    def send(self, data: str, *args, encoding: str = 'utf-8'):
        try:
            data = self.name + ': ' + data
            self.sock.send(data.encode(encoding), *args)
        except Exception as exception:
            self.commands.output(exception)

    def receive(self, *args, encoding: str = 'utf-8'):
        while not self.stop_event.is_set():
            try:
                if not args:
                    args = (4096,)
                message = self.sock.recv(*args).decode(encoding)
                if message == 'NICKNAME_REQUEST':
                    self.sock.send(self.name.encode('utf-8'))
                else:
                    self.commands.output(message)
            except OSError:
                pass
            except Exception as exception:
                self.commands.output(exception)
                self.exit()
