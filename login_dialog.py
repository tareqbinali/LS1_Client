import keyring
import re
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QVBoxLayout, QCheckBox, QMessageBox, QLabel, QFormLayout, QDateEdit
)
from PySide6.QtGui import QFont

# Set a font size for the button
font = QFont("Arial", 8)


class LoginDialog(QDialog):
    def __init__(self, db, table_name):
        super().__init__()
        self.setWindowTitle("Login")
        
        self.table_name=table_name
        self.db = db

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.remember_me = QCheckBox("Remember me", self)

        self.login_button = QPushButton("Login", self)
        self.login_button.setFont(font)
        self.login_button.clicked.connect(self.check_credentials)

        # layout = QVBoxLayout()
        # layout.addWidget(self.username_input)
        # layout.addWidget(self.password_input)
        # layout.addWidget(self.remember_me)
        # layout.addWidget(self.login_button)
        
        layout = QFormLayout()
        layout.addRow(QLabel("email :"), self.username_input)
        layout.addRow(QLabel("password:"), self.password_input)
        layout.addRow(self.remember_me)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)

        self.setMinimumWidth(400)  # Minimum width for the dialog
        layout.setContentsMargins(20, 20, 20, 20)  # Set margins
        layout.setSpacing(10)  # Set spacing between elements

        self.load_saved_credentials()

    def load_saved_credentials(self):
        """Load saved credentials from keyring if available."""
        saved_username = keyring.get_password(self.table_name, "saved_username")
        saved_password = keyring.get_password(self.table_name, saved_username) if saved_username else None

        if saved_username and saved_password:
            self.username_input.setText(saved_username)
            self.password_input.setText(saved_password)
            self.remember_me.setChecked(True)


    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()

        self.status, self.user, self.header =self.db.verify_password(self.table_name, username, password)
        if self.status:
            if self.remember_me.isChecked():
                keyring.set_password(self.table_name, "saved_username", username)
                keyring.set_password(self.table_name, username, password)
            else:
                keyring.delete_password(self.table_name, "saved_username")
                keyring.delete_password(self.table_name, username)

            self.accept()  # Close dialog on success
            self.db.update_cell(self.table_name, 'last_login', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.user[0])

        else:
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()

    # def show_register_dialog(self):
    #     register_dialog = RegisterDialog(self.db)
    #     if register_dialog.exec():
    #         QMessageBox.information(self, "Success", "Registration successful! You can now log in.")

class RegisterDialog(QDialog):
    def __init__(self, db, table_name):
        super().__init__()
        self.setWindowTitle("Register")
        self.db = db
        self.table_name=table_name

        # Create input fields
        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)

        # Password inputs
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        # Register button
        self.register_button = QPushButton("Register", self)
        self.register_button.clicked.connect(self.register_user)
        self.register_button.setFont(font)

        # Layout for form inputs
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("First Name:"), self.first_name_input)
        form_layout.addRow(QLabel("Last Name:"), self.last_name_input)
        form_layout.addRow(QLabel("Email:"), self.email_input)
        form_layout.addRow(QLabel("Password:"), self.password_input)
        form_layout.addRow(QLabel("Confirm Password:"), self.confirm_password_input)

        # Register button
        form_layout.addWidget(self.register_button)

        # Set layout to form layout
        self.setLayout(form_layout)

        # Set dialog width and spacing
        self.setMinimumWidth(400)  # Minimum width for the dialog
        form_layout.setContentsMargins(20, 20, 20, 20)  # Set margins
        form_layout.setSpacing(10)  # Set spacing between elements

    def register_user(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        email = self.email_input.text()
        # dob = self.dob_input.date().toString("yyyy-MM-dd")
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not first_name or not last_name or not email or not password:
            QMessageBox.warning(self, "Error", "All fields must be filled.")
            return

        if not self.is_valid_email(email):
            QMessageBox.warning(self, "Error", "Invalid email format.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        # success = self.db.insert_user(self.table_name, 
        #     (first_name, last_name, email, dob, "*", "*", "review", "User", "SpecGrid", password)
        # )
        # if self.db.check_email_id("Licence_App", email):
        #      QMessageBox.warning(self, "Error", "User already exists!")
        #      return

        if self.db.check_entry(self.table_name, email, column_name='email_id'):
            QMessageBox.warning(self, "Error", "User already exists!")
            return
        
       
        # Get the current date
        current_date = datetime.now()
        # Add 90 days
        expiry_date = current_date + timedelta(days=90)
        # success=self.db.insert_user(self.table_name, (first_name, last_name, email, "2025-05-08","*", "*", "review", "User", 'SpecGrid', password))
        success=self.db.insert_user(
            self.table_name, 
            first_name=first_name, 
            last_name=last_name, 
            email_id=email, 
            password=password, 
            role='user', 
            status='review',
            app_name='SpecGrid', 
            expiry_date=expiry_date.strftime(('%Y/%m/%d')),
            reg_date=current_date.strftime('%Y-%m-%d %H:%M:%S')
        )

        if success:
            self.accept()
            QMessageBox.information(self, "Success", "Registration completed!")
            
        else:
            QMessageBox.critical(self, "Error", "Failed to register user.")

    def is_valid_email(self, email):
        """ Check if email format is valid. """
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email)
