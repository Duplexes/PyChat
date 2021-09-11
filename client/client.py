import socket
import threading


class Client:
    def __init__(self, host: str, port: int, nickname: str, sock: socket.socket = None):
        self.host = host
        self.port = port
        self.nickname = nickname
        self.sock = sock if sock is not None else socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0, None)
        self.sock.settimeout(1)
        self.stop_event = threading.Event()

    def start(self):
        self.sock.connect((self.host, self.port))
        self.receive_thread = threading.Thread(target=self.receive, daemon=True)
        self.receive_thread.start()

    def stop(self):
        self.stop_event.set()
        self.sock.close()

    def send(self, data: str, *args, encoding: str = 'utf-8'):
        if data:
            data = f'{self.nickname}: {data}'
            self.sock.send(data.encode(encoding), *args)

    def receive(self, *args, encoding: str = 'utf-8') -> str:
        while not self.stop_event.is_set():
            try:
                if not args:
                    args = (4096,)
                message = self.sock.recv(*args).decode(encoding)
                if message == 'NICKNAME_REQUEST':
                    self.sock.send(self.nickname.encode('utf-8'))
                else:
                    print(message)
            except OSError:
                pass
            except Exception as exception:
                print(f"Exception: {exception}")
                self.stop()
