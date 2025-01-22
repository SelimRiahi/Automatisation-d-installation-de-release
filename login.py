from PyQt5.QtWidgets import QMessageBox,QDesktopWidget,QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import Qt
import sys
import os
import subprocess

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")

        self.username_label = QLabel("Username:")
        self.username_entry = QLineEdit()
        self.username_layout = QVBoxLayout()
        self.username_layout.addWidget(self.username_label)
        self.username_layout.addWidget(self.username_entry)

        self.password_label = QLabel("Password:")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password) 
        self.password_layout = QVBoxLayout()
        self.password_layout.addWidget(self.password_label)
        self.password_layout.addWidget(self.password_entry)

        self.login_button = QPushButton("Log in")
        self.login_button.setFixedHeight(35)
        self.login_button.setFixedWidth(120)  # Set the height of the button
        self.login_button.clicked.connect(self.login)
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.username_layout)
        self.layout.addLayout(self.password_layout)
        self.layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)
        self.resize(470, 330)   
        self.center()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())    

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to Wizardd.py
        wizardd_path = os.path.join(current_dir, 'Wizardd.py')

        if username == 'admin' and password == 'admin':
            # Open the source code in VS Code
            subprocess.Popen(['code', wizardd_path])
            self.close()
        elif username == 'user' and password == 'user':
            # Run the main application
            subprocess.Popen(['python3', wizardd_path])
            self.close()
        else:
                QMessageBox.warning(self, 'Error', 'Incorrect username or password. Please try again.')
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.login_button.click()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #333;
            color: #fff;
            font-family: 'Arial';
        }
        QPushButton {
            background-color: #555;
            border: 2px solid #fff;
            border-radius: 5px;
            padding: 5px;
            color: #fff;
        }
        QPushButton:hover {
            background-color: #777;
        }
        QLineEdit {
            background-color: #555;
            border: 2px solid #fff;
            border-radius: 5px;
            padding: 5px;
            color: #fff;
        }
    """)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())