from PySide6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QVBoxLayout, QCheckBox, QMessageBox
)
from PySide6.QtCore import QSettings

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("Login")
        self.db = db  # Store the database connection object

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.save_password_checkbox = QCheckBox("Save Password", self)

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.check_credentials)

        layout = QVBoxLayout()
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.save_password_checkbox)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.load_credentials()  # Load saved credentials

    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Verify credentials using the database function
        if self.db.verify_password("LS1_Licence_App", username, password):
            if self.save_password_checkbox.isChecked():
                self.save_credentials(username, password)
            else:
                self.clear_saved_credentials()
            self.accept()  # Close dialog on success
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()

    def save_credentials(self, username, password):
        """ Save username and password using QSettings. """
        settings = QSettings("MyCompany", "MyApp")
        settings.setValue("username", username)
        settings.setValue("password", password)

    def load_credentials(self):
        """ Load saved credentials, if available. """
        settings = QSettings("MyCompany", "MyApp")
        username = settings.value("username", "")
        password = settings.value("password", "")
        
        self.username_input.setText(username)
        self.password_input.setText(password)
        self.save_password_checkbox.setChecked(bool(password))

    def clear_saved_credentials(self):
        """ Clear stored username and password. """
        settings = QSettings("MyCompany", "MyApp")
        settings.remove("username")
        settings.remove("password")
