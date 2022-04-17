import pickle
import socket

from utils import Messenger, log


class Client(Messenger):
    def __init__(self, ip=None, port=None,
                 message_signal=None, info_signal=None):
        super().__init__(ip, port, message_signal)
        self.info_signal = info_signal
        self.server_info = list()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection.settimeout(2)

    def connect(self, propagate=False):
        if self.address == (None, None):
            log.error(f"[{self}] No address used")
        try:
            log.info(f"[{self}] Trying to connect to {self.address}")
            self.connection.settimeout(10)
            self.connection.connect(self.address)
            self.connection.settimeout(2)
            self.connected = True
            self.connection.send(pickle.dumps(("info", self.name)))
        except (ConnectionError, socket.timeout):
            log.warning("Could not reach host")
            if propagate:
                raise

    def _run(self):
        while self.connected:
            try:
                data = self.connection.recv(4096)
                if data == b'':
                    self.connected = False
                    break
                else:
                    command, value = pickle.loads(data)
                    if command == "message":
                        self.message = value
                    elif command == "info":
                        self.server_info = value
                        if self.info_signal is not None:
                            self.info_signal.emit()
            except socket.timeout:
                pass
            except ConnectionError:
                self.connected = False
        log.info(f"{self} stops listening")

    def send_message(self, message: str):
        if self.connected:
            try:
                data = ("message", message)
                self.connection.send(pickle.dumps(data))
            except ConnectionError:
                log.warning(f"[{self}] Connection failed")
            except AttributeError:
                log.warning(f"[{self}] Sending failed, not connected")
        else:
            log.warning(f"[{self}] Not connected")

    def closing_statement(self):
        self.connection.send(pickle.dumps(("info", "remove")))

    def __str__(self):
        return "Client"


if __name__ == '__main__':
    client = Client("127.0.0.1", 7878)
    client.connect()
    client.run()
