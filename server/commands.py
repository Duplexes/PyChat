import shlex
from server import Server


class Commands:
    def __init__(self, ui):
        try:
            from cli import UI
            self.ui: UI = ui
        except ImportError:
            self.ui = ui
        self.server = Server(self)

    def input(self, value: str):
        try:
            if value.startswith('/'):
                command = shlex.split(value[1:])
                if command and not command[0].startswith('_'):
                    getattr(self, command[0], self.default)(*command[1:])
            else:
                self.server.send_to_clients(value)
        except Exception as exception:
            self.ui.output(exception)

    def output(self, value: str):
        self.ui.output(value)

    def default(self, *args):
        """Unknown command."""
        self.ui.output(self.default.__doc__)

    def help(self, *args):
        """Print a list of commands."""
        if args and args[0] in dir(self):
            self.ui.output(getattr(self, args[0]).__doc__)
        else:
            self.ui.output("Type 'help <command>' for information about a specific command.")
            self.ui.output("Available commands:")
            for member in dir(self):
                if not member.startswith('_'):
                    self.ui.output('\t' + str(member))

    def host(self, host = '', port = 6675, *args):
        """Start hosting."""
        self.server.start(host, int(port))

    def stop(self, *args):
        """Stop the server."""
        self.server.stop()
        self.ui.stop()

    def exit(self, *args):
        """Forcefully exit."""
        self.server.exit()
        self.ui.stop()
