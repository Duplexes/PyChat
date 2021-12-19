import socket
from threading import Thread, Event
from pyngrok import ngrok


class Client:
    def __init__(self, host: str, port: int, sock: socket.socket):
        self.host = host
        self.port = port
        self.sock = sock
        self.name = self.get_name()

    def send(self, data: str, *args, encoding: str = 'utf-8'):
        self.sock.send(data.encode(encoding), *args)

    def receive(self, *args, encoding: str = 'utf-8') -> str:
        if not args:
            args = (4096,)
        return self.sock.recv(*args).decode(encoding)

    def get_name(self) -> str:
        self.send('NICKNAME_REQUEST')
        return self.receive()


class Server:
    def __init__(self, commands, sock: socket.socket = None):
        try:
            from commands import Commands
            self.commands: Commands = commands
        except ImportError:
            self.commands = commands
        try:
            self.name = "Server"
            self.sock = sock if sock is not None else socket.socket()
            self.sock.settimeout(1)
            self.clients: list[Client] = []
            self.client_threads: list[Thread] = []
            self.stop_event = Event()
            self.idle_thread = Thread(target=self._idle, daemon=False, name='IdleThread')
            self.idle_thread.start()
            self.listener_thread = Thread(target=self.accept_clients, daemon=True, name='ListenerThread')
            self.commands.output("Server initialized")
        except Exception as exception:
            self.commands.output(exception)

    def _idle(self):
        while not self.stop_event.is_set():
            pass

    def start(self, host: str = 'localhost', port: int = 6675):
        try:
            self.host = host
            self.port = port
            self.sock.bind((self.host, self.port))
            self.sock.listen()
            public_url = str(ngrok.connect(self.port, 'tcp', options={'remote_addr': f'{self.host}:{self.port}'}).public_url)
            self.remote_host = public_url.split('//')[1].split(':')[0]
            self.remote_port = public_url.split(':')[2]
            self.commands.output("Server started")
            self.commands.output(f"Local host: {self.host if self.host != '' else 'localhost'}")
            self.commands.output(f"Local port: {self.port}")
            self.commands.output(f"Remote host: {self.remote_host}")
            self.commands.output(f"Remote port: {self.remote_port}")
            self.listener_thread.start()
        except Exception as exception:
            self.commands.output(exception)

    def stop(self):
        self.send_to_clients("Server closed")
        self.commands.output("Server closed")
        self.stop_event.set()
        self.sock.close()

    def exit(self):
        self.stop_event.set()
        raise SystemExit

    def send_to_clients(self, data: str, clients: list[Client] = [], *args, encoding: str = 'utf-8'):
        if not clients:
            clients = self.clients
        self.commands.output(data)
        for client in clients:
            client.send(data, *args, encoding=encoding)

    def accept_clients(self):
        while not self.stop_event.is_set():
            try:
                connection, address = self.sock.accept()
                client = Client(host=address[0], port=address[1], sock=connection)
                if client.name in [client.name for client in self.clients]:
                    self.commands.output(f"Failed to connect with client '{client.name}' {client.host}:{client.port}: Nickname already exists")
                    client.send(f"Connection refused: nickname {client.name} already exists")
                    client.sock.close()
                else:
                    self.commands.output(f"Established connection with client: '{client.name}' {client.host}:{client.port}")
                    self.clients.append(client)
                    self.send_to_clients(f"{client.name} joined")
                    thread = Thread(target=self.handle_client, args=(client,), name=f'clnthndlr-{client.name}', daemon=True)
                    self.client_threads.append(thread)
                    thread.start()
            except OSError:
                pass
            except Exception as exception:
                self.commands.output(f"Exception: {exception}")
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
                self.send_to_clients(f"{client.name} left due to error: {exception}")
                break
