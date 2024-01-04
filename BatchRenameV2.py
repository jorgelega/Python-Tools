import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget, QLineEdit, QPushButton, QVBoxLayout, \
    QWidget, QHBoxLayout, QLabel
from PyQt5 import QtGui  # Import QtGui module


# List of allowed image file extensions
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp','.exr','.tga','.svg','.psd','.ai','.pic','.rat']

class BatchRenameTool(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Batch Rename Tool")
        self.setGeometry(100, 100, 1000, 600)  # Adjust the size as needed

        # Central Widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Dark Theme Styling
        self.setStyleSheet(
            "QMainWindow {background-color: #2E2E2E; color: #FFFFFF; font-size: 24px;}"
            "QListWidget {background-color: #424242; border: none; color: #FFFFFF; font-size: 18px;}"
            "QLineEdit {background-color: #363636; color: #FFFFFF; border: 1px solid #6E6E6E; font-size: 24px;}"
            "QPushButton {background-color: #007ACC; color: #FFFFFF; border: none; padding: 10px 20px; font-size: 24px;}"
            "QPushButton:hover {background-color: #0064A2;}"
            "QLabel { background-color: #424242; color: #FFFFFF; font-size: 20px; padding: 10px; }"
        )

        # Layout
        layout = QVBoxLayout()

        # File List
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Directory Label and Input Field
        directory_layout = QHBoxLayout()
        self.directory_input = QLineEdit()
        self.directory_input.setPlaceholderText("Select or enter directory path")
        directory_layout.addWidget(self.directory_input)
        self.select_folder_button = QPushButton("Select Folder")
        directory_layout.addWidget(self.select_folder_button)
        layout.addLayout(directory_layout)

        # Input Fields
        input_layout = QHBoxLayout()
        name_input = QLineEdit()
        name_input.setObjectName('new_name')
        name_input.setPlaceholderText("New Name")
        suffix_input = QLineEdit()
        suffix_input.setObjectName('suffix')
        suffix_input.setPlaceholderText("Suffix")
        padding_input = QLineEdit()
        padding_input.setPlaceholderText("0-6")
        padding_input.setValidator(QtGui.QIntValidator(0, 6))  # Allow only numbers from 0 to 6
        padding_input.setText("4")  # Default padding value
        input_layout.addWidget(name_input)
        input_layout.addWidget(suffix_input)
        input_layout.addWidget(padding_input)  # Add the padding input field
        layout.addLayout(input_layout)

        # Buttons
        button_layout = QHBoxLayout()
        rename_button = QPushButton("Rename")
        button_layout.addWidget(rename_button)
        layout.addLayout(button_layout)

        # Connect Buttons to Functions
        self.select_folder_button.clicked.connect(self.select_folder)
        rename_button.clicked.connect(self.rename_files)

        central_widget.setLayout(layout)

    def select_folder(self):
        folder = self.directory_input.text()
        if not folder:
            folder = QFileDialog.getExistingDirectory(self, "Select a Folder")
        if folder:
            self.select_folder_button.setStyleSheet('background-color: #2A612A;')  # Set button background color to green

            self.folder = folder
            self.directory_input.setText(folder)  # Update the QLineEdit with the selected folder path
            self.load_files()

    def load_files(self):
        self.file_list.clear()
        if hasattr(self, 'folder'):
            files = os.listdir(self.folder)
            self.file_list.addItems(files)
            image_files = [file for file in files if os.path.splitext(file)[-1].lower() in ALLOWED_IMAGE_EXTENSIONS]

    def rename_files(self):
        if hasattr(self, 'folder'):
            new_name = self.findChild(QLineEdit, 'new_name').text()
            suffix = self.findChild(QLineEdit, 'suffix').text()
            padding = int(self.padding_input.text())  # Get the padding value from the input field
            current_index = 0  # Initialize the index to 0
        for index in range(self.file_list.count()):
            current_index += 1  # Increment the index
            old_file_name = os.path.join(self.folder, self.file_list.item(index).text())
            file_extension = os.path.splitext(old_file_name)[-1].lower()
            if file_extension in ALLOWED_IMAGE_EXTENSIONS:
                new_file_name = os.path.join(self.folder,
                                             f"{new_name}_{suffix}_{index + 1:0{padding}d}{file_extension}")  # Use padding
                os.rename(old_file_name, new_file_name)
        self.load_files()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BatchRenameTool()
    window.show()
    sys.exit(app.exec_())
