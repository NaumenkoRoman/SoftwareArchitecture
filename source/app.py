import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton

facade_service_address = 'http://localhost:8080'

class MyApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.console = None
        self.post_button = None
        self.get_button = None
        self.text_area = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Enter your message...")

        self.post_button = QPushButton("Send Message")
        self.post_button.clicked.connect(self.on_post_button_clicked)

        self.get_button = QPushButton("Get Message Logs")
        self.get_button.clicked.connect(self.on_get_button_clicked)

        self.console = QTextEdit()
        self.console.setPlaceholderText("Requests' results will be displayed here...")
        self.console.setReadOnly(True)

        layout.addWidget(self.text_area)
        layout.addWidget(self.post_button)
        layout.addWidget(self.get_button)
        layout.addWidget(self.console)
        self.setLayout(layout)
        self.setWindowTitle('Client UI')
        self.setGeometry(500, 500, 500, 300)

    def on_post_button_clicked(self):
        input_text = self.text_area.toPlainText()
        url = facade_service_address + "/message"
        data = {"msg": f"{input_text}"}
        try:
            response = requests.post(url, json=data)
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        if response.status_code == 200:
            self.console.append(f"Success: {response.json()}")
        else:
            self.console.append(f"Failed with status code: {response.status_code}")

    def on_get_button_clicked(self):
        url = facade_service_address + "/message"
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        if response.status_code == 200:
            self.console.append(f"Success: {response.json()}")
        else:
            self.console.append(f"Failed with status code: {response.status_code}")

def main():
    app = QApplication(sys.argv)
    window = MyApplication()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
