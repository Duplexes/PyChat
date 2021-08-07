import socket
import threading
import pyco
from pyngrok import ngrok

host = ''
port = 6675
print("Server starting...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print("Starting connection to ngrok...")
public_url = ngrok.connect(port, 'tcp')
print(f"Server connection info: ")
print(f"{public_url}")
clients = []
nicknames = []


def broadcast(message: str, clients):
    print(message)
    for client in clients:
        client.send(message.encode('utf-8'))


def handle_client(client: socket.socket):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            broadcast(message, [x for x in clients if x != client])
        except Exception as exception:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left due to error: {exception}', clients)
            nicknames.remove(nickname)
            break


def accept_client():
    while True:
        client, address = server.accept()
        print(f"Established connection with client: {address}")
        client.send('NICKNAME_REQUEST'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        print(f"Client nickname: {nickname}")
        broadcast(f"{nickname} joined!", clients)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


if __name__ == '__main__':
    accept_client()