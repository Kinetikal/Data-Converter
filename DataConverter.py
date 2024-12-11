from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QTextEdit, QProgressBar, QStatusBar, QCheckBox,
                             QFileDialog, QMessageBox, QSizePolicy, QTreeView, QFileSystemModel, QSpinBox)
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QDropEvent
from PySide6.QtCore import QThread, Signal, QObject, QDir, QFile, QTextStream, QSettings
from pathlib import Path
import re
import zipfile
import os
import sys
import time
from datetime import datetime

# Directory where the script is located
basedir = os.path.dirname(__file__)

class Worker(QObject):
    progress_updated = Signal(int)
    log_message = Signal(str)
    finished = Signal()
    show_message = Signal(str, str)

    def __init__(self, parent, input_folder, output_folder, patterns, compression_method, delete_logfiles_after_zipping, ignore_younger_than, ignore_older_than):
        super().__init__()
        self.parent = parent
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.patterns = patterns
        self.compression_method_text = compression_method  
        self.delete_logfiles_checkbox = delete_logfiles_after_zipping
        self.ignore_younger_than = ignore_younger_than
        self.ignore_older_than = ignore_older_than
        
        if compression_method  == "zlib (Fast)":
            self.compression_method = zipfile.ZIP_DEFLATED
        elif compression_method  == "bz2 (Good)":
            self.compression_method = zipfile.ZIP_BZIP2
        elif compression_method  == "lzma (Highest)":
            self.compression_method = zipfile.ZIP_LZMA

    def run(self):
        try:
            start = time.process_time()
            counter = 0 # Counter to display compressing archive 1 out of n
            for pattern in self.patterns:
                counter += 1 # Updating the counter
                regex = f"^{re.escape(pattern).replace('\\*', '.*')}$"
                # Only .log files - Change in the future maybe to any filetype = remove f.endswith(".log"), pattern must then end like this "*.<some_filetype> e.x. (*.xlsx, *.txt, *.mp3 etc...)"
                matching_files = [f for f in os.listdir(self.input_folder) if f.endswith(".log") and re.match(regex, f)] 
                now = datetime.now()
                filtered_files = []
                
                for file in matching_files:
                    file_path = os.path.join(self.input_folder, file)
                    creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    file_age = (now - creation_time).days
                    
                    if (self.ignore_younger_than is None or file_age >= self.ignore_younger_than) and \
                        (self.ignore_older_than is None or file_age <= self.ignore_older_than):
                        filtered_files.append(file)
                        
                total_files = len(matching_files)
                
                if filtered_files:
                    # Print processing message
                    self.log_message.emit(f"Starting to compress log files with compression method: {self.compression_method_text}")
                    creating_archive_message = f"Creating archive {pattern.replace('*', '')}.zip ({counter}/{len(self.patterns)})"
                    self.log_message.emit(len(creating_archive_message) * "-")
                    self.log_message.emit(creating_archive_message)
                    self.log_message.emit(len(creating_archive_message) * "-")
                    # Continue processing
                    zip_filename = f"{pattern.replace('*', '')}.zip"
                    zip_path = os.path.join(self.output_folder, zip_filename)
                    self.log_message.emit("Starting zipping of log files...")
                    with zipfile.ZipFile(zip_path, "w", compression=self.compression_method) as zipf:
                        for index, file in enumerate(matching_files):
                            file_path = os.path.join(self.input_folder, file)
                            zipf.write(file_path, arcname=file)
                            if self.delete_logfiles_checkbox:
                                os.unlink(file_path) # Deletes zipped log files
                            self.log_message.emit(f"Zipping file {file}")
                            progress = int((index + 1) / total_files * 100)
                            self.progress_updated.emit(progress)
                    
                    elapsed = time.process_time() - start
                    
                    if self.delete_logfiles_checkbox:
                        task_complete_message = f"\nTask completed - Created archive '{zip_filename}' with {len(matching_files)} files.\nCleaning up - Deleted {len(matching_files)} log files that were zipped.\nElapsed time: {round(elapsed, 2)} seconds."
                        self.log_message.emit(task_complete_message)
                    else:
                        task_complete_message = f"\nTask completed - Created archive '{zip_filename}' with {len(matching_files)} files.\nElapsed time: {round(elapsed, 2)} seconds."
                        self.log_message.emit(task_complete_message)
                else:
                    self.log_message.emit(f"No files found matching pattern(s): {pattern}")
                    self.finished.emit()
                    
            self.finished.emit()
            self.show_message.emit("Zipping Completed", "Zipping process completed successfully.")  
            
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.log_message.emit(message)
            self.show_message.emit("An exception occurred", message)  
            self.finished.emit()

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
        self.setGeometry(500, 250, 800, 700)
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
        layout = QVBoxLayout(central_widget)
        
        horizontal_layout = QHBoxLayout()

    

    
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
