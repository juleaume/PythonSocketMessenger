from typing import Union

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, \
    QGroupBox, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, \
    QTextEdit

from utils import get_available_hosts, log, Messenger


class ServerConfigurator(QGroupBox):
    def __init__(self, name, ip_type=QLineEdit, see_server_info=False):
        super().__init__(name)
        layout = QVBoxLayout()
        self.setLayout(layout)
        ip_layout = QHBoxLayout()
        ip_label = QLabel("IP")
        ip_layout.addWidget(ip_label, 1, Qt.AlignRight)
        if ip_type == QLineEdit:
            self.ip_selector = QLineEdit("127.0.0.1")
            self.address_button = QPushButton("Connect")
            self.ip_selector.returnPressed.connect(self.address_button.click)
        else:
            self.ip_selector = QComboBox()
            self.ip_selector.addItems(get_available_hosts())
            self.address_button = QPushButton("Create")

        ip_layout.addWidget(self.ip_selector, 2, Qt.AlignLeft)
        layout.addLayout(ip_layout)

        port_layout = QHBoxLayout()
        port_label = QLabel("Port")
        port_layout.addWidget(port_label, 1, Qt.AlignRight)
        self.port_selector = QLineEdit("7878")
        self.port_selector.returnPressed.connect(self.address_button.click)
        port_layout.addWidget(self.port_selector, 2, Qt.AlignLeft)
        layout.addLayout(port_layout)

        layout.addWidget(self.address_button)

        self.server_info = TextShow()
        if see_server_info:
            layout.addWidget(self.server_info)

    @property
    def ip(self):
        if isinstance(self.ip_selector, QComboBox):
            return self.ip_selector.currentText()
        else:
            return self.ip_selector.text()

    @ip.setter
    def ip(self, value):
        if isinstance(self.ip_selector, QComboBox):
            self.ip_selector.setCurrentText(value)
        else:
            self.ip_selector.setText(value)

    @property
    def port(self):
        return int(self.port_selector.text())

    @port.setter
    def port(self, value):
        self.port_selector.setText(f"{value}")


class MessageBox(QGroupBox):
    def __init__(self, parent, name):
        super().__init__(name)
        self.parent = parent  # type: QMainWindow
        self.endpoint = None  # type: Union[None, Messenger]
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.text_history_box = TextShow()
        layout.addWidget(self.text_history_box)
        text_layout = QHBoxLayout()
        self.user_text_message_box = QLineEdit()
        self.user_text_message_box.setEnabled(False)
        text_layout.addWidget(self.user_text_message_box, 2)
        self.send_button = QPushButton("???")
        self.send_button.setFixedWidth(30)
        self.send_button.clicked.connect(self._send_and_place)
        text_layout.addWidget(self.send_button, 1, Qt.AlignBottom)

        self.user_text_message_box.returnPressed.connect(
            self.send_button.click)

        layout.addLayout(text_layout)

    def _send_and_place(self):
        if self.endpoint is None:
            log.error("Not connected")
            return
        msg = self.user_text_message_box.text()
        self.user_text_message_box.setText('')
        if msg:
            signed_msg = f"[{self.endpoint.name}] {msg}\n"
            self.endpoint.send_message(signed_msg)
            self.append_message(signed_msg)

    def append_message(self, message):
        self.text_history_box.insertPlainText(message)
        self.text_history_box.moveCursor(QTextCursor.End)

    def update_text(self):
        if self.endpoint is not None:
            self.append_message(self.endpoint.message)
        else:
            log.error("Endpoint is not connected")

    def connect(self, endpoint):
        self.endpoint = endpoint


class TextShow(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        e.ignore()
