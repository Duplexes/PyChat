# import time
import socket
import threading
# from pyco import cursor, terminal, NonBlockingInput


class Client(socket.socket):
    def __init__(self, host: str, port: int, nickname: str, family: socket.AddressFamily = socket.AF_INET, type: socket.SocketKind = socket.SOCK_STREAM, proto: int = 0, fileno: int = None):
        super().__init__(family, type, proto, fileno)
        self.host = host
        self.port = port
        self.nickname = nickname
        self.connect((host, port))
        # self.input_line = terminal.get_size().lines - 1
        # self.last_output_line = cursor.get_position()[0]

    def start(self):
        self.wait = threading.Event()
        self.send_thread = threading.Thread(target=self.send_str)
        self.send_thread.start()
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def send_str(self):
        while True:
            message = self.input()
            if message is not None and message != '':
                message = f'{self.nickname}: {message}'
                super().send(message.encode('utf-8'))
                self.output(message)

    def receive(self):
        while True:
            try:
                message = self.recv(1024).decode('utf-8')
                if message == 'NICKNAME_REQUEST':
                    self.send(self.nickname.encode('utf-8'))
                else:
                    self.output(message)
            except Exception as exception:
                self.output(f"An error occured: {exception}")

    def input(self) -> str:
        return input()

        # Attempt at making the input line at the bottom of the terminal screen
        # Doesnt work cause theres 2 threads using the terminal window,
        # and when cursor.get_position() is called while another thread is using input(),
        # everything breaks

        # cursor.set_position(0, self.input_line)
        # time.sleep(0.1)
        # terminal.clear_line()
        # self.message = None

        # def set_message(data):
        #     self.message = data

        # input_thread = NonBlockingInput(callback=set_message, daemon=True, prefix='> ')
        # input_thread.start()
        # while True:
        #     if self.message is not None or self.wait.is_set():
        #         input_thread.stop()
        #         input_thread.join()
        #         break

        # cursor.set_position(0, self.input_line)
        # terminal.clear_line()
        # return self.message

    def output(self, message: str):
        print(message)

        # Attempt at making output text print above the input line

        #self.wait.set()
        #cursor.save_position()
        #cursor.set_position(0, self.last_output_line)
        #terminal.clear_line()
        #print(message)
        #self.last_output_line = cursor.get_position()[0]
        #if self.input_line - self.last_output_line < 5:
        #    terminal.scroll_up(1)
        #    self.last_output_line -= 1
        #cursor.restore_position()
        #self.wait.clear()


if __name__ == '__main__':
    host = input("Remote host: ")  # '127.0.0.1'
    port = int(input("Remote port: "))  # 6675
    nickname = input("Nickname: ")  # 'client1'
    client = Client(host, port, nickname)
    client.start()
