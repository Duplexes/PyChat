import socket
import threading
from pyngrok import ngrok
from typing import Union


class Client:
    def __init__(self, sock: socket.socket, address: tuple[str, int]):
        self.sock = sock
        self.address = address
        self.nickname = self.get_nickname()

    def send(self, data: Union[bytes, str], *args, encoding: str = 'utf-8'):
        if type(data) == str:
            data = data.encode(encoding)
        self.sock.send(data, *args)

    def send_file(self, filename: str, *args, encoding: str = 'utf-8'):
        with open(filename, 'rb') as file:
            self.send(file.read(), *args, encoding=encoding)

    def recv_str(self, *args, encoding: str = 'utf-8') -> str:
        return self.sock.recv(*args).decode(encoding)

    def get_nickname(self) -> str:
        self.send('NICKNAME_REQUEST')
        return self.recv_str(1024)


class Server:
    def __init__(self, host: str = '', port: int = 6675, sock: socket.socket = None):
        self.nickname = "Server"
        self.host = host
        self.port = port
        self.sock = sock if sock is not None else socket.socket()
        self.sock.bind((host, port))
        self.sock.listen()
        self.clients: list[Client] = []
        public_url = str(ngrok.connect(port, 'tcp', options={'remote_addr': f'{host}:{port}'}).public_url)
        self.remote_host = public_url.split('//')[1].split(':')[0]
        self.remote_port = public_url.split(':')[2]
        self.output(f"Local host: {self.host if self.host != '' else 'localhost'}")
        self.output(f"Local port: {self.port}")
        self.output(f"Remote host: {self.remote_host}")
        self.output(f"Remote port: {self.remote_port}")

    def start(self):
        self.accept_clients()

    def input(self):
        pass

    def output(self, message):
        print(message)

    def send_to_all(self, data: Union[bytes, str], clients: list[Client], *args, encoding: str = 'utf-8'):
        if type(data) == bytes:
            data = data.decode(encoding)
        self.output(data)
        for client in clients:
            client.send(data.encode(encoding), *args, encoding=encoding)

    def accept_clients(self):
        while True:
            conn, addr = self.sock.accept()
            client = Client(sock=conn, address=addr)
            if client.nickname in [client.nickname for client in self.clients]:
                self.output(f"Failed to connect with client '{client.nickname}' {client.address}: Nickname already exists")
                client.send(f"Connection refused: nickname {client.nickname} already exists")
                client.sock.close()
            else:
                self.output(f"Established connection with client: '{client.nickname}' {client.address}")
                self.clients.append(client)
                self.send_to_all(f"{client.nickname} joined", self.clients)
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()

    def handle_client(self, client: Client):
        while True:
            try:
                message = client.recv_str(1024)
                self.send_to_all(message, [x for x in self.clients if x != client])
            except Exception as exception:
                client.sock.close()
                self.clients.remove(client)
                self.send_to_all(f'{client.nickname} left due to error: {exception}', self.clients)
                break


if __name__ == '__main__':
    server = Server()
    server.start()
