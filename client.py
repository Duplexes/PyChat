import socket
import threading
import pyco

host = input("Host: ")
port = int(input("Port: "))
nickname = input("Nickname: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICKNAME_REQUEST':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        except Exception as exception:
            print(f"An error occured: {exception}")
            client.close()
            break


def send():
    while True:
        message = f'{nickname}: {input()}'
        client.send(message.encode('utf-8'))


receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=send)
write_thread.start()