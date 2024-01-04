import sys
import os
import secrets
import string
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QListWidget, QStyledItemDelegate, QListWidgetItem, QRadioButton, QTextEdit
from PySide2.QtCore import Qt, QMimeData
from PySide2.QtGui import QColor
from cryptography.fernet import Fernet

class PasswordGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.main_directory = None  # Initialize main_directory attribute
        self.encryption_key = None  # Initialize encryption_key attribute

        self.directory_label = QLabel(self)  # Define directory_label
        self.init_ui()  # Initialize the user interface

        self.load_main_directory()  # Load the main directory path and encryption key
        self.load_encryption_key()  # Load the encryption key

        if self.encryption_key is None:
            # Generate a new encryption key if it doesn't exist
            self.encryption_key = Fernet.generate_key()
            self.save_encryption_key()  # Save the encryption key securely

        self.refresh_listbox()  # Refresh the listbox on program load

        self.cipher_suite = Fernet(self.encryption_key)  # Initialize the cipher suite with the key

    def init_ui(self):
        self.setWindowTitle("Password Generator")
        self.setGeometry(100, 100, 800, 1500)  # Adjust the window size

        # Dark theme style with reduced font size (30% smaller)
        self.setStyleSheet("""
            background-color: #303030;
            color: #FFFFFF;
            font-size: 25px;  /* 30% smaller font size */
        """)

        layout = QVBoxLayout()

        self.account_input = QLineEdit(self)
        self.account_input.setPlaceholderText("Enter Account Name")
        self.account_input.setStyleSheet("border: 2px solid #696969;")
        layout.addWidget(self.account_input)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setStyleSheet("border: 2px solid #696969;")
        layout.addWidget(self.username_input)

        self.use_custom_password_radio = QRadioButton("Custom Password", self)

        self.use_custom_password_radio.toggled.connect(self.toggle_password_input)
        layout.addWidget(self.use_custom_password_radio)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter Custom Password")
        self.password_input.setStyleSheet("border: 2px solid #696969;")

        self.password_input.setEnabled(False)  # Initially disabled
        layout.addWidget(self.password_input)

        # Save Password button with green background and padding
        self.save_button = QPushButton("Save Password", self)
        self.save_button.clicked.connect(self.save_password)
        self.save_button.setStyleSheet("background-color: #16462B; color: #BEBEBE; padding: 10px; height: 80px;")
        layout.addWidget(self.save_button)

        # Generate Password button with blue background and padding
        self.generate_button = QPushButton("Generate Password", self)
        self.generate_button.clicked.connect(self.generate_password)
        self.generate_button.setStyleSheet("background-color: #162E46; color: #BEBEBE; padding: 10px; height: 40px;")
        layout.addWidget(self.generate_button)

        self.password_label = QLabel(self)
        self.password_label.setAlignment(Qt.AlignCenter)
        self.password_label.setStyleSheet("font-size: 30px; color: #00D7C1; padding: 20px 0;")

        layout.addWidget(self.password_label)

        # Copy Password button with orange background and padding
        self.copy_button = QPushButton("Copy Password", self)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setStyleSheet("background-color: #4D4D4D; color: #BEBEBE; padding: 10px; height: 40px;")
        layout.addWidget(self.copy_button)

        # Select Directory button with dark black background and padding
        self.load_button = QPushButton("Select Directory", self)
        self.load_button.clicked.connect(self.load_password)  # Fixed method name
        self.load_button.setStyleSheet("background-color: #4D4D4D; color: #BEBEBE; padding: 10px; height: 40px;")
        layout.addWidget(self.load_button)

        # Define directory_label here
        layout.addWidget(self.directory_label)

        self.listbox = QListWidget(self)
        self.listbox.setItemDelegate(StyledItemDelegate(self.listbox))  # Custom delegate for styling
        self.listbox.itemDoubleClicked.connect(self.load_password)
        layout.addWidget(self.listbox)

        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.refresh_listbox)
        self.refresh_button.setStyleSheet("background-color: #4D4D4D; color: #BEBEBE; padding: 10px; height: 40px;")
        layout.addWidget(self.refresh_button)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Enter Text (Codes)")
        self.text_edit.setStyleSheet("border: 2px solid #696969;")
        layout.addWidget(self.text_edit)

        self.copy_codes_button = QPushButton("Copy Codes", self)
        self.copy_codes_button.clicked.connect(self.copy_text_to_clipboard)
        self.copy_codes_button.setStyleSheet("background-color: #4D4D4D; color: #BEBEBE; padding: 10px; height: 40px;")
        layout.addWidget(self.copy_codes_button)

        self.setLayout(layout)
    def toggle_password_input(self):
        if self.use_custom_password_radio.isChecked():
            self.generate_button.setEnabled(False)
            self.password_input.setEnabled(True)
        else:
            self.generate_button.setEnabled(True)
            self.password_input.setEnabled(False)

    def generate_password(self):
        while True:
            length = 25  # Adjusted to 25 characters
            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(characters) for _ in range(length))
            if len(password) >= 25:
                self.generated_password = password
                self.password_label.setText(password)
                break

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setText(self.generated_password)
        clipboard.setMimeData(mime_data)

    def save_password(self):
        account_name = self.account_input.text()
        username = self.username_input.text()
        plaintext_password = self.generated_password if not self.use_custom_password_radio.isChecked() else self.password_input.text()
        codes = self.text_edit.toPlainText()  # Get the text from QTextEdit

        if not account_name or not username or not plaintext_password:
            return

        if not self.main_directory:
            QMessageBox.warning(self, "Directory Not Set", "Please select a main directory first.")
            return

        # Encrypt the plaintext password and codes before saving them
        encrypted_password = self.cipher_suite.encrypt(plaintext_password.encode()).decode()
        encrypted_codes = self.cipher_suite.encrypt(codes.encode()).decode()

        # Save the encrypted password and codes to a file in the main directory
        filename = os.path.join(self.main_directory, f"{account_name}_{username}_password.txt")
        with open(filename, 'w') as file:
            file.write(f"Encrypted Password: {encrypted_password}\nEncrypted Codes: {encrypted_codes}")

        # Clear input fields
        self.account_input.clear()
        self.username_input.clear()
        if self.use_custom_password_radio.isChecked():
            self.password_input.clear()
        self.text_edit.clear()

        QMessageBox.information(self, "Success", "Password and Codes saved successfully!")

    def load_password(self, item):
        data = item.data(Qt.UserRole)  # Retrieve the full item data
        lines = data.split('\n')

        encrypted_password = None
        encrypted_codes = None

        for line in lines:
            if line.startswith("Encrypted Password: "):
                encrypted_password = line.replace('Encrypted Password: ', '')
            elif line.startswith("Encrypted Codes: "):
                encrypted_codes = line.replace('Encrypted Codes: ', '')

        if encrypted_password:
            # Ask the user if they want to view the original password
            response = QMessageBox.question(self, "View Original Password", "Do you want to view the original password?", QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.Yes:
                # Decrypt the encrypted password and display it
                try:
                    plaintext_password = self.cipher_suite.decrypt(encrypted_password.encode()).decode()
                    self.password_label.setText(plaintext_password)
                    self.generated_password = plaintext_password
                except Exception as e:
                    self.password_label.setText("Error decrypting password")
            else:
                self.password_label.setText("Password is encrypted")

        if encrypted_codes:
            # Decrypt the encrypted codes and display them
            try:
                plaintext_codes = self.cipher_suite.decrypt(encrypted_codes.encode()).decode()
                self.text_edit.setPlainText(plaintext_codes)
            except Exception as e:
                self.text_edit.clear()
        else:
            self.text_edit.clear()

    def refresh_listbox(self):
        if self.main_directory:
            self.listbox.clear()
            for root, _, files in os.walk(self.main_directory):
                for file in files:
                    if file.endswith("_password.txt"):
                        parts = os.path.splitext(file)[0].split('_')
                        if len(parts) >= 3:
                            account_name = ' '.join(parts[:-2])
                            username = parts[-2]
                            with open(os.path.join(root, file), 'r') as file:
                                data = file.read()
                                item = QListWidgetItem(f"Account: {account_name}\nUsername: {username}")
                                item.setData(Qt.UserRole, data)  # Store the full item data as user data
                            self.listbox.addItem(item)

    def save_main_directory(self):
        # Save the selected main directory path to a text file
        main_dir_path = os.path.join("C:\\", "password_directory")  # Correct directory name
        if not os.path.exists(main_dir_path):
            os.makedirs(main_dir_path)
        with open(os.path.join(main_dir_path, "main_directory.txt"), 'w') as file:
            file.write(self.main_directory)

    def load_main_directory(self):
        # Load the selected main directory path from the text file
        main_dir_path = os.path.join("C:\\", "password_directory")  # Correct directory name
        if os.path.exists(main_dir_path):
            try:
                with open(os.path.join(main_dir_path, "main_directory.txt"), 'r') as file:
                    self.main_directory = file.read()
                    if os.path.exists(self.main_directory):
                        self.directory_label.setText(f"Selected Directory: {self.main_directory}")
            except FileNotFoundError:
                pass

    def save_encryption_key(self):
        main_dir_path = os.path.join("C:\\", "password_directory")
        if not os.path.exists(main_dir_path):
            os.makedirs(main_dir_path)
        with open(os.path.join(main_dir_path, "encryption_key.txt"), 'wb') as file:
            file.write(self.encryption_key)

    def load_encryption_key(self):
        main_dir_path = os.path.join("C:\\", "password_directory")
        key_path = os.path.join(main_dir_path, "encryption_key.txt")
        if os.path.exists(key_path):
            with open(key_path, 'rb') as file:
                self.encryption_key = file.read()

    def copy_text_to_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setText(self.text_edit.toPlainText())
        clipboard.setMimeData(mime_data)

class StyledItemDelegate(QStyledItemDelegate):
    def __init__(self, list_widget):
        super().__init__(list_widget)
        self.list_widget = list_widget

    def paint(self, painter, option, index):
        if index.row() % 2 == 1:  # Check if the row number is odd
            option.backgroundBrush = QColor(50, 50, 50)  # Set darker background for odd rows
        super().paint(painter, option, index)


def main():
    app = QApplication(sys.argv)
    window = PasswordGeneratorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
