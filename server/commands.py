# from server import Server


class commands:
    def __init__(self, server):
        from server import Server
        self.server: Server = server

    # @staticmethod
    def default(self, *args):
        """Unknown command."""
        print(commands.default.__doc__)

    # @staticmethod
    def start(self, host, port, *args):
        """Start hosting."""
        self.server.start(host, int(port))

    # @staticmethod
    def stop(self, *args):
        """Stop the program."""
        self.server.stop()

    # @staticmethod
    def kick(self, *args):
        """Kick a client."""
        print("Command not implemented.")

    # @staticmethod
    def password(self, *args):
        """Change the server password."""
        print("Command not implemented.")
