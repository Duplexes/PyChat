import socket
import threading
import shlex
from pyngrok import ngrok
from pyco import utils, NonBlockingInput
from commands import commands


class Client:
    def __init__(self, host: str, port: int, sock: socket.socket):
        self.host = host
        self.port = port
        self.sock = sock
        self.char_limit = 64
        self.nickname = self.get_nickname()

    def send(self, data: str, *args, encoding: str = 'utf-8'):
        self.sock.send(data.encode(encoding), *args)

    def receive(self, *args, encoding: str = 'utf-8') -> str:
        if not args:
            args = (4096,)
        data = self.sock.recv(*args).decode(encoding)
        if len(data) > self.char_limit:
            data = data[:self.char_limit]
        return utils.remove_ansi(utils.remove_control_chars(data))

    def get_nickname(self) -> str:
        self.send('NICKNAME_REQUEST')
        return self.receive()

    # def send_file(self, filename: str, *args, encoding: str = 'utf-8'):
    #     with open(filename, 'rb') as file:
    #         self.send(file.read(), *args, encoding=encoding)

    # def receive_file(self):
    #     pass


class Server:
    def __init__(self, sock: socket.socket = None):
        self.nickname = "Server"
        self.sock = sock if sock is not None else socket.socket()
        self.sock.settimeout(1)
        self.clients: list[Client] = []
        self.client_threads: list[threading.Thread] = []
        self.commands = commands(server=self)
        self.stop_event = threading.Event()
        self.input_thread = NonBlockingInput(callback=self.input, daemon=True)
        self.input_thread.start()
        input()

    def start(self, host: str = '', port: int = 6675):
        self.host = host
        self.port = port
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        public_url = str(ngrok.connect(self.port, 'tcp', options={'remote_addr': f'{self.host}:{self.port}'}).public_url)
        self.remote_host = public_url.split('//')[1].split(':')[0]
        self.remote_port = public_url.split(':')[2]
        self.output(f"Local host: {self.host if self.host != '' else 'localhost'}")
        self.output(f"Local port: {self.port}")
        self.output(f"Remote host: {self.remote_host}")
        self.output(f"Remote port: {self.remote_port}")
        self.accept_clients()

    def stop(self):
        self.stop_event.set()
        self.sock.close()

    def input(self, string: str):
        if string.startswith('/'):
            try:
                self.command(string)
            except Exception as exception:
                self.output(f"Exception: {exception}")
        else:
            self.send_to_clients(string)

    def output(self, message: str):
        print(message)

    def command(self, command: str):
        command = shlex.split(command[1:])
        if command:
            getattr(self.commands, command[0], self.commands.default)(*command[1:])

    # def clean_text(self, string: str) -> str:
    #     for char in self.illegal_chars:
    #         string.replace(char, '')
    #     return string

    def send_to_clients(self, data: str, clients: list[Client] = [], *args, encoding: str = 'utf-8'):
        if not clients:
            clients = self.clients
        self.output(data)
        for client in clients:
            client.send(data, *args, encoding=encoding)

    def accept_clients(self):
        while not self.stop_event.is_set():
            try:
                connection, address = self.sock.accept()
                client = Client(host=address[0], port=address[1], sock=connection)
                if client.nickname in [client.nickname for client in self.clients]:
                    self.output(f"Failed to connect with client '{client.nickname}' {client.host}:{client.port}: Nickname already exists")
                    client.send(f"Connection refused: nickname {client.nickname} already exists")
                    client.sock.close()
                else:
                    self.output(f"Established connection with client: '{client.nickname}' {client.host}:{client.port}")
                    self.clients.append(client)
                    self.send_to_clients(f"{client.nickname} joined")
                    thread = threading.Thread(target=self.handle_client, args=(client,), name=f'clnthndlr-{client.nickname}', daemon=True)
                    self.client_threads.append(thread)
                    thread.start()
            except OSError:
                pass
            except Exception as exception:
                self.output(f"Exception: {exception}")
                self.stop()

    def handle_client(self, client: Client):
        while not self.stop_event.is_set():
            try:
                message = client.receive()
                if not message:
                    raise Exception
                self.send_to_clients(message)
            except OSError:
                pass
            except Exception as exception:
                client.sock.close()
                self.clients.remove(client)
                self.send_to_clients(f'{client.nickname} left due to error: {exception}')
                break


if __name__ == '__main__':
    server = Server()
