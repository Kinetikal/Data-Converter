from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QTextEdit, QProgressBar, QStatusBar, QCheckBox,
                             QFileDialog, QMessageBox, QSizePolicy, QTreeView, QFileSystemModel, QSpinBox)
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QDropEvent
from PySide6.QtCore import QThread, Signal, QObject, QDir, QFile, QTextStream, QSettings
from PySide6.QtCore import Qt  # Import Qt for alignment constants
from pathlib import Path
from datetime import datetime
from pathlib import Path
import re
import zipfile
import os
import sys
import time
import pandas as pd
import csv

# Directory where the script is located
basedir = os.path.dirname(__file__)

class DraggableLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Enable dropping on QLineEdit

    def dragEnterEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # Accept the drag event
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # Accept the drag move event
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            # Extract the file path from the drop event
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.setText(file_path)
            event.acceptProposedAction()  # Accept the drop event
        else:
            event.ignore()

class MainWindow(QMainWindow):
    progress_updated = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Converter")
        self.setWindowIcon(QIcon("_internal\\icon\\data_converter.ico"))
        self.setGeometry(500, 250, 600, 500)
        self.saveGeometry()
        
        # Settings to save current location of the windows on exit
        self.settings = QSettings("App","Data Converter")
        geometry = self.settings.value("geometry", bytes())
        self.restoreGeometry(geometry)
        
        # Current theme files to set as the main UI theme
        self.theme = "_internal\\themes\\default.qss"
        
        # Initialize the .qss Theme File on startup
        self.initialize_theme(self.theme)
        
        # Initialize the UI and it's layouts
        self.initUI()
        
        # Create the menu bar
        self.create_menu_bar()
    
    def initialize_theme(self, theme_file):
        try:
            file = QFile(theme_file)
            if file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
            file.close()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Theme load error", f"Failed to load theme:\n{message}")
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QVBoxLayout(central_widget)
        
        # Horizontal Layout
        horizontal_layout = QHBoxLayout()
        
        # Vertical Layout for widgets in the horizontal layout
        vert_layout_widgets_one = QVBoxLayout()
        
        hor_layout_widgets_one = QHBoxLayout()
        hor_layout_widgets_two = QHBoxLayout()
        
        # Set up the file system model
        self.tree_view = QTreeView()
        self.tree_view.setDragEnabled(True)
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath("")
        self.file_system_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        
        # Set the model to the tree view
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(""))  # Set root index to the filesystem root
        
        # Optional: Customize the view
        self.tree_view.setColumnWidth(0, 250)  # Adjust column width
        self.tree_view.setHeaderHidden(False)   # Show the header
        self.tree_view.setSortingEnabled(True)  # Enable sorting
        
        # Widgets
        title_label = QLabel("Data Converter")
        title_label.setAlignment(Qt.AlignCenter)  # Center-align text
        title_label.setStyleSheet("font-size: 18pt; font: bold; color: #64b5f6;")

        refresh_theme_button = QPushButton("Refresh Theme")
        refresh_theme_button.clicked.connect(self.refresh_theme)
        
        self.button_load_filesystem = QPushButton("Load new path")
        self.button_load_filesystem.clicked.connect(self.load_filesystem_path)
        self.button_load_filesystem.setToolTip("Loads TreeView anew based on the inputted source folder.")
        
        combobox_text = QLabel("Select a category for the filetypes:")
        combobox_category = QComboBox()
        
        hor_layout_widgets_one.addWidget(combobox_text)
        hor_layout_widgets_one.addWidget(combobox_category)
        
        # Widgets
        from_label = QLabel("From:")
        from_combobox = QComboBox()
        to_label = QLabel("To:")
        to_combobox = QComboBox()
        
        input_file = DraggableLineEdit()
        input_file.setPlaceholderText("File to be converted...")
        
        # Add widgets to the hor_layout_widgets_two
        hor_layout_widgets_two.addWidget(from_label)
        hor_layout_widgets_two.addWidget(from_combobox)
        hor_layout_widgets_two.addWidget(to_label)
        hor_layout_widgets_two.addWidget(to_combobox)
        
        # Add widgets to the vertical layout
        vert_layout_widgets_one.addWidget(title_label)
        vert_layout_widgets_one.addLayout(hor_layout_widgets_one)
        vert_layout_widgets_one.addLayout(hor_layout_widgets_two)
        vert_layout_widgets_one.addWidget(input_file)
        
        # Add some spacing between elements
        vert_layout_widgets_one.addStretch()
        vert_layout_widgets_one.addWidget(self.tree_view)
        vert_layout_widgets_one.addWidget(self.button_load_filesystem)
        vert_layout_widgets_one.addWidget(refresh_theme_button)

        # Add the vertical layout to the horizontal layout
        horizontal_layout.addLayout(vert_layout_widgets_one)

        # Add the horizontal layout to the main layout
        main_layout.addLayout(horizontal_layout)

    
    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(self, "Exit Program", "Are you sure you want to exit the program?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        geometry = self.saveGeometry()
        self.settings.setValue("geometry", geometry)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Open Menu
        open_menu = menu_bar.addMenu("&Open")
        open_input_action = QAction("Open Input Folder", self)
        open_input_action.setStatusTip("Opens the log files input folder")
        open_input_action.triggered.connect(self.open_input_folder)
        open_menu.addAction(open_input_action)
        open_output_action = QAction("Open Output Folder", self)
        open_output_action.setStatusTip("Opens the zipped archives output folder")
        open_output_action.triggered.connect(self.open_output_folder)
        open_menu.addAction(open_output_action)
    
    # ====== Functions Start ====== #
    
    def refresh_theme(self):
        self.initialize_theme(self.theme)

    # Open Log files input folder 
    def open_input_folder(self):
        directory_path = self.input_folder.text()
        
        if os.path.exists(directory_path):
            try:
                os.startfile(directory_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(self, "Path Error", f"Path does not exist or is not a valid path:\n{directory_path}")
    
    
    # Open Zipped Archive output folder
    def open_output_folder(self):
        directory_path = self.output_folder.text()
        
        if os.path.exists(directory_path):
            try:
                os.startfile(directory_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(self, "Path Error", f"Path does not exist or is not a valid path:\n{directory_path}")

        
    def browse_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.input_folder.setText(folder)
            self.update_log_files_count(folder)
            
            
    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.output_folder.setText(folder)
            
    def load_filesystem_path(self):
        try:
            folder = QFileDialog.getExistingDirectory(self, "Select Directory")
            if folder and QDir(folder).exists():  # Ensure the folder path exists
                # Update the file system model root path and tree view root index
                self.file_system_model.setRootPath(folder)
                self.tree_view.setRootIndex(self.file_system_model.index(folder))
                print(f"Loaded folder: {folder}")
            else:
                QMessageBox.warning(self, "Warning", f"Source path does not exist or is empty:\n{folder}")
        except Exception as ex:
            print(f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
