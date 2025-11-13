# this is the main file actually
# last update 08 Mar 2025
# version_no=1.1
version_url='https://drive.google.com/uc?id=1_2T5R9TCR4qZLTGXw5ifjEsBqWlLhAEz'

# pip install fsspec for dataframe
# pip install pydub simpleaudio


gui_development=False


import sys
import os
import gc
import threading
# import traceback
# from os import walk


from constants import app_exe_path, version_no, release_date, icon_file , style_file, refresh_icon_file, client_cert_file, client_key_file
from gcpCloud import gcp 
from sql_licence import MySQLDatabase as db
from login_dialog import LoginDialog, RegisterDialog  



# To upload Spec Files Process 1:
# a)Connect and Select "Empty, NULL, None"
# b) Table>Download
# c) From ls1Audio.m Featuures>Create spectrogram need to create this from python
# d)back to python and Spectrogram>Upload spectrogram


# os.environ["QT_MULTIMEDIA_PREFERRED_BACKENDS"] = "windowsmedia"
# os.environ["QT_MULTIMEDIA_PREFERRED_BACKENDS"] = "ffmpeg"

# from PySide6.QtMultimedia import QMediaPlayer, QSoundEffect, QAudioOutput
# os.environ["QT_LOGGING_RULES"] = "qt.multimedia.*=true"

from pydub import AudioSegment
AudioSegment.ffmpeg = None
import simpleaudio as sa
# import pygame

# player = QMediaPlayer()
# audio_output = QAudioOutput()
# player.setAudioOutput(audio_output)


# import tempfile

from PySide6 import QtCore
# from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QToolBar,QGroupBox, QHBoxLayout, QVBoxLayout,\
     QGridLayout, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,QScrollArea,QLineEdit,\
     QMessageBox, QFileDialog, QProgressBar, QDialog, QDialogButtonBox, QTextEdit, QLabel,\
     QInputDialog, QMenu,  QCalendarWidget, QHeaderView,  QStackedLayout, QDateEdit,\
     QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsPathItem, QSizePolicy
     

from PySide6.QtCore import QSize, QThread, Signal, Qt, QDate, QTimer, QObject,\
     Slot, QUrl, QCoreApplication, QPoint, QPointF, QFile, QTextStream, QSettings

from PySide6.QtGui import QAction, QIcon, QPixmap, QFont, QKeyEvent,  QPainter, QColor, QPen, QPainterPath, QTextCursor



# from audio_player import AudioPlayer  # Import AudioPlayer class



# from multipleInputDialog import inputDialog
# from audio_functions import *


# from sqlDatabase import sql
# from updateApp import updateApp
# from progressAnimation import AnimationWidget



import datetime
import requests



import re
import pickle
import json
import csv

import glob
import configparser

import time
import io

from PIL import Image #Pillow
# import wave
# import array

# import shutil

bucket_name="ls1-sample.appspot.com"
licence_table_name="Licence_App"
last_search=None
WorkingFile=""
Folder=r"C:\Wi"


# following is needed since after the compilation the icon_file goes to _internal folder
meipass_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
# file_path = os.path.join(meipass_path, "C:\Dropbox\PythonProject\GCPClient", "icon.png") # this is needed if the "icon.png" file resides in a different folder
# icon_file = os.path.join(meipass_path, "icon.png")

config=configparser.ConfigParser()

import logging



if getattr(sys, 'frozen', False): # .exe file
    import pyi_splash
    developer=False
else:
    developer=True

def setup_logging(text_widget):
    """ Configures logging to output to both self.text_debug and a file. """
    
    log_location=os.path.join(Folder, 'logs',  'ls1')
    os.makedirs(log_location, exist_ok=True)
    log_filename = os.path.join(log_location,f"{datetime.datetime.now().strftime('%Y-%m-%d')}-ls1-client.log")

    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)  # Capture all logs
    logger.setLevel(logging.INFO)  # Logs INFO and above (INFO, WARNING, ERROR, CRITICAL)

    # Remove existing handlers to prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # File Handler (Logs to log_filename)
    file_handler = logging.FileHandler(log_filename, mode="a")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    # QTextEdit Handler (Logs to GUI)
    gui_handler = QTextEditHandler(text_widget)
    gui_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    # Console Handler (Logs to console)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    # Attach handlers
    logger.addHandler(file_handler)
    logger.addHandler(gui_handler) 
    logger.addHandler(console_handler)  # Log to console   

    # logging.basicConfig(
    #     filename=log_filename,
    #     level=logging.INFO,  # Logs INFO and above (INFO, WARNING, ERROR, CRITICAL)
    #     format="%(asctime)s - %(levelname)s - %(message)s",
    #     datefmt="%Y-%m-%d %H:%M:%S"
    # )

    # logging.debug('This is a debug message')
    # logging.info('This is an info message')
    # logging.warning('This is a warning message')
    # logging.error('This is an error message')
    # logging.critical('This is a critical message')    


def open_file_dialog(location=None,title="Open File", ext='pkl', type="Model files"):
    file_dialog = QFileDialog()
    file_dialog.setWindowTitle(title)
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    if location!=None:
        file_dialog.setDirectory(location)  # Set the default directory
    
    file_dialog.setNameFilter(f"{type} (*.{ext});;All files (*)")

    if file_dialog.exec():
        selected_files = file_dialog.selectedFiles()
        print("Selected file:", selected_files[0])
        return selected_files[0]
    else:
        return None

def time_stamp():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return timestamp

def currentTime():
    upload_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return upload_datetime

def splitPath(FullPath):
    dir_name = os.path.dirname(FullPath)
    file_name = os.path.basename(FullPath)
    base_name, ext = os.path.splitext(file_name)
    return dir_name, base_name, ext

# def newFileName(filename, ext='.wav', newlocation=None):
#     location, filename, _=splitPath(filename)
#     if newlocation:
#         location=newlocation
#     return os.path.join(location, filename + ext)


# def createFilename(RecFilename, LoggerSN, Folder, tag='.wav'):
#     filename,_=os.path.splitext(RecFilename)
#     blob_name=LoggerSN + '_' + filename + tag
#     filename=os.path.join(Folder, blob_name)
#     return filename, blob_name



# def locationFromURL(wav_url, rootfolder="audio/"):
#     url = urllib.parse.unquote(wav_url)
#     start_index = url.find(rootfolder)
#     last_index = url.rfind('/')
#     cloudfolder= url[start_index:last_index]
#     return cloudfolder     



def saveToCSV2(data, file_path=None):
    # file_path=os.path.join(Folder, 'data.csv')

    with open(file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for row in data:
            csv_writer.writerow(row)

def saveToCSV(data, filename=None, header=None, confirm=False):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:  # Use utf-8 encoding
            writer = csv.writer(csvfile)
            if header:
                # Write the header row
                writer.writerow(header)

            # Write the data rows
            for row in data:
                writer.writerow(row)
        logging.info(f"Data successfully saved to {filename}!")
        if confirm:
            msgBox(f'saved as {filename}', 'done', 'done')

    except Exception as e:
        logging.info(f"An error occurred: {e}")            

def readFromCSV(filename, read_header=False):
    header=[]
    data=[]
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:  # Use utf-8 encoding
            reader = csv.reader(csvfile)
            if read_header:
                header = next(reader)  # Read the first row as header
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"An error occurred: {e}")
    return data, header


# def readFromCSV2(file_path=None):
#     # file_path=os.path.join(Folder, 'data.csv')
#     data = []
#     with open(file_path, 'r') as csvfile:
#         csv_reader = csv.reader(csvfile)
#         for row in csv_reader:
#             data.append(row)
#     return data
    

# def saveSettings(data_settings):
#     # # Write the ConfigParser object to a file
#     # with open(ConfigFile, 'w') as f:
#     #     config.write(f)
#         # Open a text file for writing
#     # with open(settings_file, 'w') as file:
#     #     # Iterate over the dictionary items and write them to the file
#     #     for key, value in data_settings.items():
#     #         if isinstance(value, str):
#     #             value="'" + value + "'"
#     #         file.write(f'{key} = {value}\n')
#     # Save the dictionary to a pickle file
#     with open(settings_file, 'wb') as file:
#         pickle.dump(data_settings, file)

#     print("file saved as " + settings_file)        

# def readSettings():
#     # # Initialize an empty dictionary
#     # settings = {}
#     # # Open the text file for reading
#     # with open(settings_file, 'r') as file:
#     #     # Read each line from the file
#     #     for line in file:
#     #                 # Split each line into key and value using the '=' character
#     #         key, value = map(str.strip, line.split('=', 1))
#     #         if not value:
#     #             value = ''
#     #         # Add the key-value pair to the dictionary
#     #         settings[key] = value
#     # Load the dictionary from the pickle file
#     with open(settings_file, 'rb') as file:
#         settings = pickle.load(file)
    
#     return settings        

# FullPath=os.path.abspath(__file__)
dir_name,base_name, ext=splitPath(os.path.abspath(__file__))
ConfigFile=os.path.join(dir_name,base_name + "_cofig.ini")
# settings_file=os.path.join(dir_name,base_name + "_setings.txt")
settings_file=os.path.join(dir_name,base_name + "_setings.pkl")



data_sample = [("Red", "#FF0000"),
          ("Green", "#00FF00"),
          ("Blue", "#0000FF"),
          ("Black", "#000000"),
          ("White", "#FFFFFF"),
          ("Electric Green", "#41CD52"),
          ("Dark Blue", "#222840"),
          ("Yellow", "#F9E56d")]

def dateFromURL(string_to_search):
    # string_to_search = "https://firebasestorage.googleapis.com/v0/b/ls1-sample.appspot.com/o/audio%2F220608X007%2F2023-05-02%2F64257973_output.wav?alt=media&token=8d61b166-6bef-4d35-a4ad-d3fa34455190"
    pattern = r"\d{4}-\d{2}-\d{2}"  # Regular expression pattern to match "YYYY-MM-DD" format

    matches = re.findall(pattern, string_to_search)
    if matches:
        # print("Matching date found:", matches[0])
        return matches[0]
    else:
        # print("No matching date found.")
        return None

# def filenameFromURL(url):
#     # url = "https://firebasestorage.googleapis.com/v0/b/ls1-sample.appspot.com/o/spectrogram%2F220812X013_64F5CF1A_spec.png?alt=media&token=b0632ba3-5953-4c7b-a748-f721b5e4aeb9"
#     # Parse the URL
#     parsed_url = urlparse(url)
#     # Get the path from the URL
#     path = parsed_url.path
#     # Split the path to get the filename
#     filename = path.split("/")[-1]
#     # Decode any URL encoding in the filename
#     filename = unquote(filename)
#     filename = filename.split("/")[-1]
#     return filename            

def dateFromLoggerSN(LoggerSN):
    date_string = LoggerSN[:6]
    date = datetime.datetime.strptime(date_string, '%y%m%d')
    formatted_date = date.strftime('%Y-%m-%d') 
    return formatted_date   


def searchFile(dir_path, file_name):
    matches=[]
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            if file_name in name:
                matches.append(os.path.join(root, name))
    if matches:
        print(f"{len(matches)} matched files:")
        for file in matches:
            print(file)
        if len(matches)>1:
            file=listBox(matches, "please select a file")
            if file:
                return file
            else:
                return None 
        else:
            return file   
    else:
        print("no match found") 
        return None           
                

def singleInput(InputStr=None, TitleStr='input', width=300, height=100,default=None):
    global last_search
    dialog = QInputDialog()
    if InputStr is not None:
        dialog.setLabelText(InputStr)
    dialog.setWindowTitle(TitleStr)
    if last_search is not None:
        dialog.setTextValue(str(last_search))
    elif default:
        dialog.setTextValue(str(default))    
    dialog.setFixedSize(width, height)
    # my_pixmap = QPixmap("icon.png")
    # my_icon = QIcon(my_pixmap)
    # dialog.setWindowIcon(my_icon)
    # dialog.show()
    ok=dialog.exec()
    if ok:
        text=dialog.textValue()
        text=text.lstrip()
        text=text.rstrip()
        if text:
            last_search=text
            return text
        else:
            return None
    else:
        return None
    
  

def msgConfirm(s, TitleStr='msg'):
    msg=QMessageBox()
    msg.setText(s)
    # msg.setWindowTitle(TitleStr)
    # my_pixmap = QPixmap("icon.png")
    # my_icon = QIcon(my_pixmap)
    # msg.setWindowIcon(my_icon)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)
    response=msg.exec()
    return response==QMessageBox.Yes
def msgBox(s, TitleStr='message', icon_type=None):
    msg = QMessageBox()
    msg.setWindowTitle(TitleStr)
    if icon_type=='error':
        msg.setIcon(QMessageBox.Critical)
    if icon_type=='done':
        msg.setIcon(QMessageBox.Information)    
    # Set the main message
    # msg.setText("An error occurred!")

    # Optionally, add additional information
    # msg.setInformativeText("Please check your input and try again.")
    # my_pixmap = QPixmap("icon.png")
    # my_icon = QIcon(my_pixmap)
    # msg.setWindowIcon(my_icon)
    if isinstance(s, list):
        s=list2String(s)
    msg.setText(s)
    msg.exec()

def dirStructure(Folder, list_widget, filename=None):
    list_widget.setProperty("Folder", Folder)
    struct=os.listdir(Folder)
    struct.insert(0, f"<<--   {Folder}")
    list_widget.clear()
    list_widget.addItems(struct)
    if filename:
        list_widget.setCurrentRow(struct.index(filename))
    wav_files = glob.glob(f"{Folder}/*.wav")
    
    item = list_widget.item(0)
    item.setText(item.text() + f" ({len(wav_files)}-wav file)")
    
    parent=list_widget.parent()
    while parent:
        if isinstance(parent, QMainWindow):
            main_window = parent
            break
        parent = parent.parent()
    parent.setWindowTitle(f"{list_widget.toolTip()} : .wav file {len(wav_files)}") 

    list_widget.setToolTip(Folder)
        

def selectFile(ext=None):
    global WorkingFile, Folder
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly  # If you want to open the file in read-only mode

    if ext:
        filter_text = f"{ext} Files (*.{ext});;All Files (*)"
    else:
        filter_text = "All Files (*)"

    # filter_text = "All Files (*)" 
    if os.path.isfile(WorkingFile):
        # filter_text = f"{WorkingFile};;{filter_text}"
        InitialFile=WorkingFile
    else:
        InitialFile=Folder
      
    selected_file, _ = QFileDialog.getOpenFileName(None, "Open File", InitialFile, filter_text, options=options)
    if selected_file:
        WorkingFile=selected_file
        return selected_file  # Return the selected file path
    else:
        return None  # Return None if no file was selected

# def readExcelFile(file_path, sheet_name=None):
#     try:
#         workbook = openpyxl.load_workbook(file_path)

#         # sheet_name = "Checked List"
#         if sheet_name:
#         # Access the sheet using get_sheet_by_name
#             sheet = workbook.get_sheet_by_name(sheet_name)
#         else:
#             sheet = workbook.active  # Assuming you want to read the active sheet
        
#         data = []
#         for row in sheet.iter_rows(values_only=True):
#             data.append(row)

#         return data

#     except Exception as e:
#         return None        

def listBox(items, TitleStr="Select an item", width=500, height=300):
    # use listBox instead of SelectDialog
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    dialog = QDialog()
    dialog.setWindowTitle(TitleStr)
    dialog.setFixedSize(width, height)
    # my_pixmap = QPixmap("icon.png")
    # my_icon = QIcon(my_pixmap)
    # dialog.setWindowIcon(my_icon)
    layout = QVBoxLayout()
    list_widget = QListWidget()
    
    for item in items:
        list_widget.addItem(QListWidgetItem(item))
    layout.addWidget(list_widget)

    # Create a QHBoxLayout for the buttons
    button_layout = QHBoxLayout()
    # Create the first QPushButton
    button1 = QPushButton("OK")
    # Add the first button to the layout
    button_layout.addWidget(button1)
    # Create the second QPushButton
    button2 = QPushButton("CANCEL")
    # Add the second button to the layout
    button_layout.addWidget(button2)
    # Add the button_layout to the main layout
    layout.addLayout(button_layout) 
    
    dialog.setLayout(layout)
    
    result = None
    
    def on_item_double_clicked(item):
        nonlocal result
        result = item.text()
        dialog.accept()

    button1.clicked.connect(on_item_double_clicked)
      
    list_widget.itemDoubleClicked.connect(on_item_double_clicked)
    
    dialog.exec()
    
    return result   


#  FUNCTIONS
def find_indices(list_to_check, item_to_find):
    indices = []
    for idx, value in enumerate(list_to_check):
        if value == item_to_find:
            indices.append(idx)
    return indices

def list2String(data):
    data=', '.join(data)
    return data

def filesUnderFolder(folder_path=None, ext='*.*'):
    if folder_path is None:
        folder_path=QFileDialog.getExistingDirectory()
    # List all files in the folder
    filenames = os.listdir(folder_path)
    # Filter files with extension ('.wav')
    filenames = [file for file in filenames if file.endswith(ext)]
    # Print the list of files with required extension
    file_path=[]
    for file in filenames:
        file_path.append(os.path.join(folder_path, file))
    return file_path, filenames


class QTextEditHandler(logging.Handler):
    """ Custom logging handler to redirect logs to a QTextEdit widget. """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_entry = self.format(record)
        self.text_widget.append(log_entry)  # Append log to QTextEdit
        # Move cursor to the end to ensure auto-scroll
        self.text_widget.moveCursor(QTextCursor.End)

class ListWidget(QListWidget):
    def sizeHint(self):
        s=QSize()
        s.setHeight(super(ListWidget,self).sizeHint().height()) 
        s.setWidth(self.sizeHintForColumn(0)) 

class SelectDialog(QDialog):
    # use listBox instead
    def __init__(self, items,TitleStr,id='', parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.setWindowTitle(TitleStr)
        # my_pixmap = QPixmap("icon.png")
        # my_icon = QIcon(my_pixmap)
        # self.setWindowIcon(my_icon)
        # self.setStyleSheet("background-color: #f0f8ff")

        # self.list_widget.addItems(["Item 1", "Item 2", "Item 3"])
        self.list_widget.addItems(items)
        if id:
            item = self.list_widget.item(id)
            self.list_widget.setCurrentItem(item)
        layout.addWidget(self.list_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_item(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            return current_item.text()
        return None

class CalendarDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Select a date :")
        self.setGeometry(100, 100, 400, 300)
        # my_pixmap = QPixmap("icon.png")
        # my_icon = QIcon(my_pixmap)
        # self.setWindowIcon(my_icon)

        layout = QVBoxLayout()

        # Create a QCalendarWidget
        self.calendar = QCalendarWidget()
        last_date = "2025/01/28"  # this is for example, this needs to be read from the saving
        predefined_date = QDate.fromString(last_date, "yyyy/MM/dd")
        self.calendar.setSelectedDate(predefined_date)
        # Optional: Ensure the calendar opens on the correct month/year
        self.calendar.setCurrentPage(2025, 1)



        layout.addWidget(self.calendar)

        # Create a button to select the date
        self.button = QPushButton("SELECT")
        layout.addWidget(self.button)

        self.button.clicked.connect(self.accept)

        self.setLayout(layout)

    def get_selected_date(self):
        selected_date = self.calendar.selectedDate()
        # return selected_date.toString()
        return selected_date.toString(Qt.ISODate)
    
class ScaledPixmapLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setScaledContents(True)

    def paintEvent(self, event):
        if self.pixmap():
            pm = self.pixmap()
            originalRatio = pm.width() / pm.height()
            currentRatio = self.width() / self.height()
            if originalRatio != currentRatio:
                qp = QPainter(self)
                pm = self.pixmap().scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                rect = QtCore.QRect(0, 0, pm.width(), pm.height())
                rect.moveCenter(self.rect().center())
                qp.drawPixmap(rect, pm)
                return
        super().paintEvent(event)    

class ClickableGraphicsView(QGraphicsView):
    clicked = Signal(int)  # Signal to emit when clicked

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index  # Store the index of this graphics view
        self.is_gray = False  # Track if the image is gray or normal

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:  # Check if left button is clicked
            self.clicked.emit(self.index)  # Emit the signal with the index


class animateProgressBar(QThread):
    finished = Signal(str, str)
    def __init__(self, progress_bar):
        super().__init__()  # Call the base class constructor
        self.progress_bar=progress_bar
        # Set the format to an empty string to hide the percentage
        self.progress_bar.setFormat("")
        self._stop_flag = False
    def run(self):
        n=0
        while not self._stop_flag:
            # self.finished.emit("good", "boy")
            if n>100:
                n=0
            self.progress_bar.setValue(n)
            n+=10
            time.sleep(2)

    def stop(self):
        self._stop_flag = True
        self.wait()        
    


class AudioPlayerThread(QThread):
    progress = Signal(int)  # Signal to update progress bar
    finished = Signal()     # Signal emitted when playback is done

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        print(f"Downloading: {self.url} ...")

        response = requests.get(self.url)
        if response.status_code == 200:
            audio = AudioSegment.from_file(io.BytesIO(response.content), format="wav")
            raw_data = audio.raw_data

            playback_obj = sa.play_buffer(
                raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate,
            )

            duration = audio.duration_seconds  # Total duration in seconds
            start_time = time.time()  # Record start time

            while playback_obj.is_playing():
                elapsed_time = time.time() - start_time
                progress_value = int((elapsed_time / duration) * 100)  # Calculate percentage
                self.progress.emit(progress_value)  # Emit progress update
                time.sleep(0.1)  # Update every 100ms

            self.progress.emit(100)  # Ensure it reaches 100%
            self.finished.emit()  # Notify that playback is done

        else:
            print("Failed to download the audio file")



class StatusSignal(QObject):
    sig=Signal(str, int)


  

class LogBox(QDialog):
    def __init__(self, title_str="update"):
        super().__init__()
        self.setWindowTitle(title_str)
        self.setGeometry(300, 300, 500, 300)
        # my_pixmap = QPixmap("icon.png")
        # my_icon = QIcon(my_pixmap)
        # self.setWindowIcon(my_icon)

        
        # Create a central widget
        # central_widget = QWidget()
        # self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        self.text_box = QTextEdit()
        layout.addWidget(self.text_box)
        
        self.ok_button = QPushButton("SAVE")
        # self.ok_button.clicked.connect(self.accept)
        self.ok_button.clicked.connect(self.save)
        layout.addWidget(self.ok_button)
        
        # self.cancel_button = QPushButton("Cancel")
        # self.cancel_button.clicked.connect(self.close)
        # layout.addWidget(self.cancel_button)

        self.setLayout(layout)
        # central_widget.setLayout(layout)

    def show_popup(self):
        self.exec()

    def update(self, result, title_str=None):
        self.text_box.append(result)
        if title_str:
             self.setWindowTitle(title_str)

    def save(self):
        text_content = self.text_box.toPlainText()
        file_path = "C:/wi/log_raw_upload.txt"
        with open(file_path, "w") as file:
            file.write(text_content)
    def closeEvent(self, event):
        # This is called when the X (close button) is clicked
        print("Close button (X) clicked")
        event.accept()

class ReadWorker(QThread):
    resultReady = Signal(object, object, object)  # Signal to send (data, headers)

    def __init__(self, gcp, dataset_id, tablename, selected_item):
        super().__init__()
        self.gcp = gcp
        self.dataset_id = dataset_id
        self.tablename = tablename
        self.selected_item = selected_item

    def run(self):
        """Fetch data in a separate thread to prevent UI freezing."""
        try:
            data, headers = self.gcp.read(
                dataset=self.dataset_id, 
                table=self.tablename, 
                condition_string=self.selected_item
            )
            self.resultReady.emit(data, headers, self.selected_item)  # Send data back to the main thread
        except Exception as e:
            print(f"Error fetching data: {e}")        

class SpecImageWorker(QThread):
    progress_updated = Signal(int)  # Signal to update progress bar
    add_image_signal = Signal(int, bytes)  # Signal to add images (index, image data)
    finished_signal = Signal()  # Signal when processing is complete

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.running = True  # Flag to stop thread

    def run(self):
        if not self.main_window.SpecFileURL:
            return

        for index, spec_url in enumerate(self.main_window.SpecFileURL):
            if not self.running:
                break  # Stop if requested

            # Fetch image from URL
            response = requests.get(spec_url)
            image_data = response.content

            # Emit signal to update UI in the main thread
            self.add_image_signal.emit(index, image_data)

            # Update progress bar
            progress_value = int((index + 1) / len(self.main_window.SpecFileURL) * 100)
            self.progress_updated.emit(progress_value)

            QCoreApplication.processEvents()

        gc.collect()  # Cleanup
        self.finished_signal.emit()  # Notify completion                     


class mainUI(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app=app # declare an app member 
        screen_size = app.primaryScreen().availableGeometry().size()
        if screen_size.width()>1499:
            self.resize(1500, 800)
        else:
            self.resize(screen_size.width()-10, screen_size.height()-30)

        # self.load_stylesheet("styles.qss")

        # Set up the logging configuration
        # logging.basicConfig(level=logging.INFO)
        # self.log_handler = LogHandler()
        # self.log_handler.setLevel(logging.INFO)
        # self.log_handler.message_logged.connect(self.updateLog)
        

        # Add the handler to the root logger
        # root_logger = logging.getLogger()
        # root_logger.addHandler(self.log_handler)

 
        # self.gcp=None
        self.gcp=gcp()
        self.db=db(client_cert_file, client_key_file)
        # if ml:
        # self.ml=ml(location="C:\\wi\\ls1\\Model")
        # self.ml.update_signal.connect(self.updateLogBox)
       
        self.app_full_path = os.path.abspath(sys.argv[0])

        # pygame.mixer.init()
        
        # self.check_update=updateApp(current_version=version_no,url_version=version_url,running_app= app_exe_path)

        self.Folder=r"C:\WI\LS1\Data"
        self.data=None
        self.Data=None
        self.LoggerSN= None
        self.RecFilename= None
        self.SpecURL= None
        self.WavFileURL=None
        self.AudioProfile=None

        self.RevisitList=None
        

        # self.NoiseType=None
        # self.NoiseTypes=['RE Check', 'NO Check', 'Leak', 'No Leak', 'Meter', 'Other']

        self.creat_spec_images=True

        # self.audio_player = AudioPlayer2()
        # self.audio_player.playback_finished.connect(self.on_playback_finished)


       
        self.query=None
        self.Stop=False

        self.WorkingFile=''
        self.last_file=None
        # self.applySettings()

        # self.current_page=1
        # self.items_per_page=3

        # self.fsave="C://WI//ls1_table.pkl"

        # self.sound_effect = QSoundEffect()

        self.audio_waveform_plots = []  # Store waveform plots for each cell
    
        if getattr(sys, 'frozen', False):
            self.setWindowTitle(f"LS1 processor, {version_no}")
        else:
            self.setWindowTitle(f"DEVELOPER MODE, VERSION :  {version_no}")
           
 
        # my_pixmap = QPixmap(icon_file)
        # my_icon = QIcon(my_pixmap)
        # self.setWindowIcon(my_icon)
        
        # self.setStyleSheet("background-color: #f0f8ff")
      
        self.background_thread=None

        self.worker_thread = None  # Placeholder for worker thread
        self.image_views = []

        self.create_menu()
        self.create_toolbar()
        self.create_widgets()
        # logger.info('creating layout')
        self.create_layout()


        setup_logging(self.text_debug)

        logging.info("APP started!!")

   
    # def iniThreads(self, run_function):
    #     if run_function=='create_images':
    #         self.thread_create_images=threadCreateSpecAudioImages(parent=self, run_function=run_function)
    #         self.thread_create_images.finished.connect(self.threadFinished)
    #         self.thread_create_images.start()
    #     if run_function=='download_wav_file':
    #         self.download_wav_file=threadDownload(parent=self)
    #         self.download_wav_file.finished.connect(self.threadFinished)
    #         self.download_wav_file.start()   

    #     if run_function=='upload_images':
    #         self.upload_images=threadUpload(parent=self, run_function=run_function)
    #         self.upload_images.finished.connect(self.threadFinished)
    #         self.upload_images.start()   

            
    def show_login_dialog(self):
           
        login_dialog = LoginDialog(self.db, licence_table_name)
        if login_dialog.exec():
            self.user_detail=login_dialog.user
            self.licence_header=login_dialog.header
            status_index = self.licence_header.index('status')
            if self.user_detail[status_index]=='active':
                logging.info("login successful!")
                # role_index = self.licence_header.index('role')
                # if self.user_detail[role_index]=='Admin':
                #     self.menu_bar.addMenu(self.menu_admin)

                self.menu_login.setTitle(f"😊{self.user_detail[1]} {self.user_detail[2]}")
               
                # Continue loading the main UI
                self.enable_widgets()   # for testing so it enables for the wrong password comment it after finish 
            else:
                logging.info("we are processing your registration and will email you once completed!")
                QMessageBox.information(self, "registration", "We are processing your registration and will email you once completed!")       

        else:
            logging.error("Login failed.")
            # sys.exit(0)  # Close the app if login fails

    def show_register_dialog(self):
        """ Show registration dialog and handle user registration. """
        register_dialog = RegisterDialog(self.db, licence_table_name)
        if register_dialog.exec():
            logging.info("registration information submitted!")
            # QMessageBox.information(self, "Success", "Registration information submitted!")
            # self.show_login()  # Redirect to login after successful registration
        else:
            logging.info("registration canceled.")        
               



    def enable_widgets(self, status=True):
        if status:
            # self.logout_action.setVisible(True)
            self.login_action.setVisible(False)
            self.register_action.setVisible(False)
        else:
            # self.logout_action.setVisible(False)
            self.login_action.setVisible(True)
            self.register_action.setVisible(True)
            self.menu_login.setTitle("🤔User")
            logging.info("logged out!")

        self.logout_action.setVisible(status)

        self.start_date.setEnabled(status)
        self.end_date.setEnabled(status)
        self.btn_Search.setEnabled(status)
        self.reload_action.setEnabled(status)
        # self.btn_Stop.setEnabled(status)
        self.btn_TableView.setEnabled(status)
        self.btn_GridView.setEnabled(status)
        

        self.menu_file.setEnabled(status)
        self.menu_help.setEnabled(status)

        if status==False:
            self.clear_all_graphics()
            self.clearTableWidgets()
            self.tablewidget.setEnabled(False)
            self.listRevisit.setVisible(False)


            
    def threadFinished(self):
        print("Thread execution completed")        

   
    def updateWindowTitle(self, status):
        self.setWindowTitle(status)
    
    
    # def createSpecFiles(self):
    #     Location=f"W:\Shared drives\LS1 Model Training\Old leaks to confirm"
    #     AudioFiles, fn=filesUnderFolder(Location, ext='.wav')

    #     for f_wav in AudioFiles:
    #         f_spec=newFileName(f_wav, '.png')
    #         if not os.path.isfile(f_spec):
    #             specImage(fwav=f_wav, fspec=f_spec)
    #             print(f"{f_spec} created")

    
    # def runSpecAudioProcessor(self):

    #     if self.btn_ProcessSpecAudio.text()=='STOP':
    #         self.btn_ProcessSpecAudio.setText("Process Spec/Audio")
    #         self.spec_audio_processor.running=False
    #         return
        

    #     self.progress_bar.setValue(0)
       
    #     # if self.gcp==None:
    #     # if self.gcp is None:
    #     #     from gcpClient import gcp 
    #     #     logging.info('initiating gcp')
    #     #     self.gcp=gcp()

    #     # if not ml:
    #     #     from deepLearning import ml
    #     #     self.ml=ml(location="C:\\wi\\ls1\\Model")
    #     #     self.ml.update_signal.connect(self.updateLogBox)    

    #     if self.data:
    #           if msgConfirm(f"{len(self.data)}-entry already loaded! Do you want to start processing from loaded data?", TitleStr='data found!'):
    #             re_read=False
    #           else:
    #             re_read=True  
    #     else:
    #         re_read=True
        
    #     if re_read:
    #         # self.clear_table()
    #         self.readTable(selected_item='Empty URL', dataset_id='LS1_Data',tablename='LS1_RawWavURL', pagenumber=[])
    #         start_processing=False
    #     else:
    #         start_processing=True    
        
    #     if self.data:
    #         if not start_processing:
    #             start_processing=msgConfirm(f"{len(self.data)}-entry found! Do you want to start processing?", TitleStr='data found!')

    #         if start_processing:
    #             self.btn_ProcessSpecAudio.setText("STOP")
                
    #             # self.logbox=LogBox("spec audio processor")
    #             # self.logbox.show()
                
    #             time.sleep(1)
    #             self.spec_audio_processor=SpecAudioProcessor(self.gcp,self.ml, self.LoggerSN,self.WavFileURL, self.RecFilename, self.SpecFileURL, self.AudioProfile,self.LS1Auto, self.updateCell, self.btn_ProcessSpecAudio)        
    #             self.spec_audio_processor.signal.sig.connect(self.updateLogBox)
                # self.spec_audio_processor.start()


    def readFromDatabase(self):
          
        self.read_table()
    
    def populateSpecImages(self):
        self.switchGroup(index=1)
        if self.creat_spec_images:
            # self.middle_layout.setCurrentWidget(self.group_spec)
            self.middle_layout.setCurrentWidget(self.middle_container)

            # Clear existing views if any
            self.image_views = []
            for i in reversed(range(self.plot_layout.count())):
                widget = self.plot_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)  # Detach widget
                    widget.deleteLater() # Delete widget

            # Ensure all items are removed properly
                self.plot_layout.update()
                QApplication.processEvents()

                self.image_views.clear()  # Ensure the list is empty

            
            # Create and populate graphics views dynamically based on URLs
            if self.SpecFileURL:
                for index, spec_url in enumerate(self.SpecFileURL):
                    # Create QGraphicsView and QGraphicsScene for each image viewer
                    graphics_view = ClickableGraphicsView(index=index)
                    graphics_view.setStyleSheet("""
                        QGraphicsView {
                            border-radius: 10px;
                            background-color: #181818;
                            border: 1px solid #333;
                        }
                    """)

                    graphics_scene = QGraphicsScene(graphics_view)
                    graphics_view.setScene(graphics_scene)

                    # Set fixed size for the graphics view
                    graphics_view.setFixedSize(300, 200)  # Adjust as needed

                    # Enable context menu
                    graphics_view.setContextMenuPolicy(Qt.CustomContextMenu)
                    graphics_view.customContextMenuRequested.connect(self.menu_on_graphics)

                    graphics_view.clicked.connect(self.on_graphics_view_clicked)

                    # Add to grid layout
                    row = index // 5
                    col = index % 5
                    self.plot_layout.addWidget(graphics_view, row, col)
                    self.image_views.append((graphics_view, graphics_scene))

                    # Fetch and display the image
                    response = requests.get(spec_url)
                    image_data = response.content

                    # Load the image into QPixmap
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)

                    # Update the QGraphicsScene with the new image
                    graphics_scene.clear()  # Clear any existing items
                    graphics_view.viewport().update()  # Force UI refresh

                    pixmap_item = QGraphicsPixmapItem(pixmap)
                    graphics_scene.addItem(pixmap_item)

                    # Adjust the view to fit the image
                    graphics_view.setSceneRect(pixmap.rect())
                    graphics_view.fitInView(graphics_scene.sceneRect(), Qt.KeepAspectRatio)

                    # Store the index and URLs as properties for later use
                    graphics_view.setProperty("index", index)
                    graphics_view.setProperty("spec_url", spec_url)
                    graphics_view.setProperty("wav_url", self.WavFileURL[index])

                    self.progress_bar.setValue((index+1)/len(self.SpecFileURL)*100)

                    QCoreApplication.processEvents()
                

                gc.collect() #Force garbage collection to clean up old widgets
                self.creat_spec_images=False    
        
    def add_image_to_ui(self, index, image_data):
        """Runs in the main thread to add an image to the UI."""
        # Create QGraphicsView and QGraphicsScene
        graphics_view = ClickableGraphicsView(index=index)
        graphics_view.setStyleSheet("""
            QGraphicsView {
                border-radius: 10px;
                background-color: #181818;
                border: 1px solid #333;
            }
        """)
        graphics_scene = QGraphicsScene(graphics_view)
        graphics_view.setScene(graphics_scene)
        graphics_view.setFixedSize(300, 200)

        # Set properties
        graphics_view.setContextMenuPolicy(Qt.CustomContextMenu)
        graphics_view.customContextMenuRequested.connect(self.menu_on_graphics)
        graphics_view.clicked.connect(self.on_graphics_view_clicked)

        row = index // 5
        col = index % 5
        self.plot_layout.addWidget(graphics_view, row, col)
        self.image_views.append((graphics_view, graphics_scene))

        # Load image into QPixmap and add to scene
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        graphics_scene.clear()
        graphics_view.viewport().update()

        pixmap_item = QGraphicsPixmapItem(pixmap)
        graphics_scene.addItem(pixmap_item)
        graphics_view.setSceneRect(pixmap.rect())
        graphics_view.fitInView(graphics_scene.sceneRect(), Qt.KeepAspectRatio)  


        # Store the index and URLs as properties for later use
        graphics_view.setProperty("index", index)
        graphics_view.setProperty("spec_url", self.SpecFileURL[index])
        graphics_view.setProperty("wav_url", self.WavFileURL[index]) 

        if self.RecFilename[index] in self.RevisitList:
            self.add_tick_mark(graphics_view, graphics_scene)   
        

            
    def menu_on_graphics(self, pos: QPoint):
        # Get the sender (the graphics view that triggered the menu)
        sender_view = self.sender()
        index = sender_view.property("index")  # Retrieve the index of the view
        

        # Create the context menu
        menu = QMenu()
        
        play_action = menu.addAction("play")
        # play_action.triggered.connect(lambda: self.play_plot(sender_view))
        # play_action.triggered.connect(lambda: self.play_plot_threaded(sender_view))
        play_action.triggered.connect(lambda: self.play_audio(sender_view))

        revisit_action = menu.addAction("revisit")
        revisit_action.triggered.connect(lambda: self.revisit_site(index))

        open_plot_action = menu.addAction("open")
        open_plot_action.triggered.connect(lambda: self.open_plot(index))
        
        # Show the menu at the global position
        menu.exec(sender_view.mapToGlobal(pos))

    def on_graphics_view_clicked(self, index):

        # self.text_debug.append(self.SpecFileURL[index])

        graphics_view, graphics_scene = self.image_views[index]
    
        # Check if a tick mark already exists, if not, add one; otherwise, remove it
        if hasattr(graphics_view, 'tick_item') and graphics_view.tick_item is not None:
            # If tick mark exists, remove it
            graphics_scene.removeItem(graphics_view.tick_item)
            graphics_view.tick_item = None
                # Find all items that exactly match self.RecFilename.
            items = self.listRevisit.findItems(self.RecFilename[index], Qt.MatchExactly)
            if items:
                for item in items:
                    row = self.listRevisit.row(item)
                    # Remove the item from the list widget.
                    removed_item = self.listRevisit.takeItem(row)
                    # Optionally, delete the removed_item if you no longer need it.
                    del removed_item
        else:
            # If tick mark does not exist, add one
            self.add_tick_mark(graphics_view, graphics_scene)
            self.listRevisit.addItem(self.RecFilename[index])
  

    def add_tick_mark(self, graphics_view, graphics_scene):
        # Get the scene's bounding rectangle and its center.
        scene_rect = graphics_scene.sceneRect()
        center = scene_rect.center()
        
        # Define three points for the tick mark.
        # # You can adjust these offsets to your taste.
        # start = QPointF(center.x() - 10, center.y())
        # mid   = QPointF(center.x() - 2, center.y() + 8)
        # end   = QPointF(center.x() + 10, center.y() - 8)
        
        start = QPointF(center.x() - 15, center.y())
        mid   = QPointF(center.x() - 3, center.y() + 12)
        end   = QPointF(center.x() + 15, center.y() - 12)
        
        # Create a path that moves from start to mid and then to end.
        path = QPainterPath()
        path.moveTo(start)
        path.lineTo(mid)
        path.lineTo(end)
        
        # Create a QGraphicsPathItem to display the tick mark.
        tick_item = QGraphicsPathItem(path)
        
        # Use a red pen with a defined width.
        pen = QPen(Qt.red)
        pen.setWidth(5)
        tick_item.setPen(pen)
        
        # Set a high z-value to ensure the tick mark appears on top.
        tick_item.setZValue(100)
        
        # Add the tick mark to the scene.
        graphics_scene.addItem(tick_item)
        
        # Store the tick mark in the graphics view for toggling later.
        graphics_view.tick_item = tick_item

    def start_populating_images(self):
        self.stop_action.setVisible(True)
        self.switchGroup(index=1)
        if self.creat_spec_images:
           
            """Start the worker thread."""
          
            if not self.worker_thread or not self.worker_thread.isRunning():
                self.RevisitList = [self.listRevisit.item(i).text() for i in range(self.listRevisit.count())]
                self.worker_thread = SpecImageWorker(self)
                self.worker_thread.progress_updated.connect(self.update_progress)
                self.worker_thread.add_image_signal.connect(self.add_image_to_ui)
                self.worker_thread.finished_signal.connect(self.on_worker_finished)
                self.worker_thread.start()

    def stop_populating_images(self):
        """Stop the worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.running = False  # Set flag to stop the loop
            self.worker_thread.quit()  # Gracefully exit thread
            self.worker_thread.wait() # Wait for thread to finish
            self.creat_spec_images=False
            logging.info('thread running grid images stopped!')
            self.stop_action.setVisible(False)

    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)

    def on_worker_finished(self):
        """Called when the worker finishes execution."""
        self.creat_spec_images=False
        logging.info("Image population finished!")
        self.stop_action.setVisible(False)
        


    def clear_all_graphics(self):
        """Clear all QGraphicsViews and QGraphicsScenes."""
    # Clear each QGraphicsView and its associated QGraphicsScene
        for graphics_view, graphics_scene in self.image_views:
            graphics_scene.clear()  # Clear all items from the scene
            graphics_view.viewport().update()  # Update the viewport to reflect changes

        # Optionally, clear the layout to remove views from the UI
        for i in reversed(range(self.plot_layout.count())):
            widget = self.plot_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        # Clear the image views list
        self.image_views.clear()

        # Update UI
        self.plot_layout.update()    
            
    def test_a_function(self):
        url='https://firebasestorage.googleapis.com/v0/b/ls1-sample.appspot.com/o/audio%2F221107X018%2F2025-02-04%2F6798B3A7_output.wav?alt=media&token=eedc1ded-97e6-434f-89f9-892d758e7c7d'
        
        # player = AudioPlayer()
        # player.show()
        # player.load_audio(url)
        # player.raise_()


        
        # self.audio_player.show()
            # Fetch audio from the URL
        # response = requests.get(url)
        # audio_data = io.BytesIO(response.content)

        # # Initialize pygame mixer
        # pygame.mixer.init()

        # # Load the audio data into pygame
        # pygame.mixer.music.load(audio_data)
        # pygame.mixer.music.play()

        # while pygame.mixer.music.get_busy():  # Wait for playback to finish
        #     pygame.time.Clock().tick(10)  # Check every 10 ms

    def play_audio(self, sender_view):
        url = sender_view.property("wav_url")  # Get URL
        self.audio_thread = AudioPlayerThread(url)  # Create thread
        self.audio_thread.progress.connect(self.update_progress)  # Connect progress updates
        self.audio_thread.finished.connect(lambda : self.on_finished("audio playback finished!"))  # Handle when done
        self.audio_thread.start()  # Start thread

    def play_plot_threaded(self, sender_view):
        """Run play_plot in a new thread."""
        thread = threading.Thread(target=self.play_plot, args=(sender_view,))
        thread.start()
        
    
    def play_plot(self, sender_view):
        url= sender_view.property("wav_url")
        logging.info(f"playing wav file  : {url} ...")

    

        response = requests.get(url)
        if response.status_code == 200:
            audio = AudioSegment.from_file(io.BytesIO(response.content), format="wav")

            # Convert to raw audio data
            raw_data = audio.raw_data
            playback_obj = sa.play_buffer(
                raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate,
            )
            
            playback_obj.wait_done()  # Wait until playback finishes
        else:
            logging.error("Failed to download the audio file")


        a=1

        # This works
        # response = requests.get(url)
        # audio_data = io.BytesIO(response.content)  # Convert to byte stream
        # # Load the audio using pydub
        # audio = AudioSegment.from_wav(audio_data)
        # # Play the audio using pydub and pygame
        # play(audio)


        # with open("audio.wav", "wb") as f:
        #     f.write(response.content)

        # # Play the audio using pygame
        # pygame.mixer.music.load("audio.wav")
        # pygame.mixer.music.play()


       
        # this works
        # url = QUrl(url)
        # player.setSource(url)
        # player.mediaStatusChanged.connect(on_media_status_changed)
        # player.errorOccurred.connect(on_error)

        logging.info('playback finished!')
    def on_playback_finished(self):
        print("Playback finished or stopped") 
        
           
    def on_finished(self, str):
        logging.info(str)    

    def revisit_site(self, index):
        self.listRevisit.addItem(self.RecFilename[index])
    def open_plot(self, index):
        url=self.SpecFileURL[index]
        # Fetch the image
        response = requests.get(url)

        # Check if request was successful
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            image.show()  # Opens the image using the default image viewer
        else:
            print("Failed to retrieve image:", response.status_code)

        

            
    

 
        

    def closeEvent(self, event):
        # config.set('Location','TrainFolder1', self.listTrain1.property("Folder"))
        # config.set('Location','TrainFolder2', self.listTrain2.property("Folder"))
        # config.set('Location','TestFolder', self.listTest.property("Folder"))
        
        # if self.listTrain1.isVisible():
        #    config.set('Settings','View', 'list')
        # else:
        #    config.set('Settings','View', 'table')  

        # saveSettings()
        self.quit
        # Override the close event
        # reply = self.instance().quit()
        # event.ignore()    
   
   #Statusbar
        # self.setStatusBar(QStatusBar(self))
     # Buttons
    

    # def applySettings(self, view=False):
    #     if view:
    #         dialog=inputDialog('current settings', self.settings)
    #         if dialog.exec() == QDialog.Accepted:
    #             self.settings = dialog.getInputs()
    #             saveSettings(self.settings)
    #             self.listTrain1.setProperty("Folder", self.settings['TrainFolder1'])
    #             self.listTrain2.setProperty("Folder", self.settings['TrainFolder2'])
    #             self.listTest.setProperty("Folder", self.settings['TestFolder'])
    #             self.populateListBox()
    #         else:
    #             print("Canceled")
    #     else:
    #         self.settings={}
    #         self.fsave="C://WI//ls1_table.pkl"
    #         # if os.path.isfile(ConfigFile):
    #         if os.path.isfile(settings_file):
    #             # config.read(ConfigFile)
    #             # self.TrainFolder1=config.get('Location', 'TrainFolder1')
    #             # self.TrainFolder2=config.get('Location', 'TrainFolder2')
    #             # self.TestFolder=config.get('Location', 'TestFolder')
    #             # self.Folder=config.get('Location', 'Folder')
    #             # self.WorkingFile=config.get('FileNames', 'WorkingFile')
    #             # self.ViewType=config.get('Settings', 'View')
    #             self.settings=readSettings()

                

    #         else:
    #             # Root="W:\My Drive\WI\LS1"
    #             # Folder="W:\My Drive\WI\LS1\Data"
    #             self.settings['Root']=r"C:\WI\LS1"
    #             self.settings['Folder']=r"C:\WI\LS1\Data"
    #             self.settings['TrainFolder1']=os.path.join(self.settings['Root'], "Train")
    #             self.settings['TrainFolder2']=os.path.join(self.settings['Root'], "Train")
    #             self.settings['TestFolder']=os.path.join(self.settings['Root'], "Test")
    #             self.settings['ViewType']='table'
    #             self.settings['current_page']=1
    #             self.settings['items_per_page']=3
                
    #             # config.add_section('App')
    #             # config.set('App','Version', '1.0')
    #             # config.add_section('Location')
    #             # config.set('Location','TrainFolder1', TrainFolder1)
    #             # config.set('Location','TrainFolder2', TrainFolder2)
    #             # config.set('Location','TestFolder', TestFolder)
    #             # config.set('Location','Folder', Folder)
    #             # config.add_section('FileNames')
    #             # config.set('FileNames','WorkingFile', WorkingFile)
    #             # config.add_section('Settings')
    #             # config.set('Settings','View', ViewType)
    #             saveSettings(self.settings)
        
    # def editSettings(self):
    #     a=inputDialog('curren settings', self.settings)


    # def start_long_loop(self):
    #     self.long_loop_thread.start()
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Your code to run after pressing Enter
            print("Enter pressed!")
        else:
            # Call the default keyPressEvent for all other keys
            super().keyPressEvent(event)
        a=1

    def on_header_clicked(self):
        logging.info("header clicked!")
        pass

    def menu_listbox(self,pos):
        listwidget = self.sender()
        # if listwidget.currentRow()==0:

        file=os.path.join(listwidget.property("Folder"), listwidget.selectedItems()[0].text())
        menu = QMenu()
        if listwidget.currentRow()==0:
            location_action=menu.addAction("change location")
            location_action.triggered.connect(lambda : self.set_train_folder(title_str='location', list_widget=listwidget, menu_action= location_action))
   
        else:
            # open_action = menu.addAction("open")
            # open_action.triggered.connect(lambda: self.openItem(file))
            if file.endswith(".wav"):
                # create_spec_action = menu.addAction("plot spectrogram")
                # create_spec_action.triggered.connect(lambda: self.plotSpectrogram(file))
                # create_spec_save_action = menu.addAction("save spectrogram")
                # create_spec_save_action.triggered.connect(lambda: self.plotSpectrogram(file, True))
                check_file_action = menu.addAction("check model for the file")
                check_file_action.triggered.connect(lambda: self.runModelProcessor(file=file))

            # clipboard_action = menu.addAction("copy to clipboard")
            # clipboard_action.triggered.connect(lambda: self.copyToClipboard(file))
        
        # show the context menu at the position of the mouse click
        menu.exec(listwidget.viewport().mapToGlobal(pos))



    def handleContextMenu(self,pos):
        # create a context menu
        menu = QMenu()
        selected_column = self.tablewidget.currentColumn()
        
        # if self.headers[selected_column] in ('LS1_WavFileURL', 'LS1_SpecFileURL', 'LS1_AudioProfile'):
        #     open_action = menu.addAction("open")
        #     open_action.triggered.connect(self.openItem)
       
        if self.headers[selected_column]=='LS1_NoiseType':
             for Type in self.NoiseTypes:
                option = menu.addAction(Type)
                # option.triggered.connect(lambda checked=False, option=option: self.filterNoiseType(option))
                option.triggered.connect(lambda checked=False, option=option: self.updateNoiseType(option))

                # option.triggered.connect(self.updateNoiseType)

        # elif self.headers[selected_column]=='LS1_WavFileURL':
        #     spec_action = menu.addAction("create spectogram")
        #     spec_action.triggered.connect(self.plotSpectrogram)

        # else:
        #     pass
  
        # clipboard_action = menu.addAction("copy to clipboard")
        # clipboard_action.triggered.connect(self.copyToClipboard)
        # clear_action = menu.addAction("clear current cell")
        # clear_action.triggered.connect(self.clearSpecURL)


        
        # show the context menu at the position of the mouse click
        menu.exec(self.tablewidget.viewport().mapToGlobal(pos))

                 
  
    
    def openItem(self, file):
        if not file:
            file=self.tablewidget.currentItem().text()
        os.startfile(file)

    # def copyToClipboard(self, StrToCopy=''):
    #     if not StrToCopy:
    #         StrToCopy=self.tablewidget.currentItem().text()
    #     pyperclip.copy(StrToCopy)

    def clearSpecURL(self, currentcell=''):
        # for i, row in enumerate(self.data):
        if not currentcell:
            row=self.tablewidget.currentRow()
            col=self.tablewidget.currentColumn()
            self.data[row][col] = None
            self.tablewidget.setItem(row, col, QTableWidgetItem(None))
        else:
            for i in range(len(self.data)):    
            # Replace the value in eighth column (LS1_SpecFileURL) with a new value
                self.data[i][7] = None
                self.tablewidget.setItem(i, 7, QTableWidgetItem((self.data[i][7])))          
    def filterNoiseType(self, Type):
        # menu_item = sender()  # Get the menu item that was clicked
        Type = Type.text() 
        NoiseType=[row[5] for row in self.data]
        data=None        
        if Type=='ALL':
            data=self.data
        else:    
            id = [i for i in range(len(NoiseType)) if NoiseType[i] ==Type] # to find an item
            if id:
               data = [self.data[i] for i in id]
        if data:
            self.populateTable(data, self.headers)        
    def searchFile(self):
        file=singleInput("Please provide file name : ", "search")
        if file:
            file=searchFile(Root, file)
            if file:
                folder, fn=os.path.split(file)
                dirStructure(folder, self.listTest, fn)
       
     


    def update_title(self, i, L):
        self.setWindowTitle(f"Current Value: {i} (L: {L})")    
       

 
    # =======================MENU FUNCTIONS=========================================
    def open_revisit_list(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self, "open file", Folder, "CSV Files (*.csv);;AllFiles (*)"
        )

        if file_name:
            self.data, self.headers=readFromCSV(file_name, read_header=True)
            # header_file=os.path.join(Folder, 'headers.json')
            # with open(header_file, "r") as file:
            #     self.headers = json.load(file)

            if self.data:
                # self.switchGroup(index=0)
                self.populateTable()
                self.populateHeaders() 
                self.listRevisit.addItems(self.RecFilename) 
                
                self.RevisitList=self.RecFilename  

    def save_revisit_list(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,                  # Parent widget
            "Save data",           # Dialog title
            Folder,                   # Default directory (empty for current directory)
            "CSV Files (*.csv);;All Files (*)"  # File filters
        )

        rec_filenames = [self.listRevisit.item(i).text() for i in range(self.listRevisit.count())]
        revisit_data = [row for row in self.data if row[1] in rec_filenames]
        saveToCSV(revisit_data, filename=file_name, header=self.headers, confirm=True)

        self.RevisitList=rec_filenames
        # if not os.path.isfile(header_file):
        #     with open(header_file, "w") as file:
        #         json.dump(self.headers, file, indent=4)
    def exportJobList(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,                  # Parent widget
                "Save revisit data",           # Dialog title
                Folder,                   # Default directory (empty for current directory)
                "CSV Files (*.csv);;All Files (*)"  # File filters
            )
            
            if file_name:
            
                # if self.gcp==None:
                #     logging.info('initiating gcp')
                #     self.gcp=gcp() 

                # rec_filenames = ["653FCD6B.RAW", "6798B3A7.RAW", "6798B471.RAW", "6798B337.RAW"]
                rec_filenames = [self.listRevisit.item(i).text() for i in range(self.listRevisit.count())]
                # Convert the list of filenames into a comma-separated string enclosed in quotes
                rec_filenames_str = ", ".join(f"'{filename}'" for filename in rec_filenames)
                # Construct the query
                query = f"SELECT * FROM LS1_Data.LS1_MainData WHERE Rec_Filename IN ({rec_filenames_str})"    

                # table_id='LS1_Data.LS1_MainData'
                # RecFilename='653FCD6B.RAW'
                # query = f"SELECT * FROM {table_id} WHERE Rec_Filename = '{RecFilename}'"
                # query = f"SELECT DMA, Client, GPS_Address, GPS_Location FROM {table_id} WHERE Rec_Filename = '{RecFilename}'"
                # Extracting Data from Main
                # query = f"SELECT * FROM LS1_Data.LS1_MainData WHERE DMA = 'Test'"
                # rec_filenames= [row[header.index('Rec_Filename')] for row in data]
                # query = f"SELECT * FROM LS1_Data.LS1_RawWavURL WHERE LS1_RecFilename IN ({rec_filenames_str})"
                # [data,header]=self.gcp.read('LS1_Data', 'LS1_RawWavURL', '',query)
                
                [data,header]=self.gcp.read(query=query)
                if data:
                    saveToCSV(data, filename=file_name, header=header, confirm=True)
        except Exception as e:
            logging.info(f'error : {e}')
            self.updateLogBox()

    def clear_job_list(self):
        rec_filenames = [self.listRevisit.item(i).text() for i in range(self.listRevisit.count())]

        for index in range(len(self.image_views)):
            graphics_view, graphics_scene = self.image_views[index]
            if hasattr(graphics_view, 'tick_item') and graphics_view.tick_item is not None:
                graphics_scene.removeItem(graphics_view.tick_item)
                graphics_view.tick_item = None
        
        self.listRevisit.clear()        



# ====================================================================================== 


    
   

    # def openURL(self):
    #     selected_row=self.tablewidget.currentRow()
    #     selected_column = self.tablewidget.currentColumn()
    #     selected_item = self.tablewidget.item(selected_row, selected_column)
    #     if selected_item is not None:
    #         selected_text = selected_item.text()
    #         if selected_text.startswith("https://"):
    #             webbrowser.open(selected_text)
    # def deleteFilesFromPC(self):
    #     LoggerSN= [row[0] for row in self.TableData]
    #     RecFilename= [row[1] for row in self.TableData]
    #     response=SelectDialog(RecFilename, 'delete the follwing files?')
    #     if response.exec() == QDialog.Accepted:
    #         L=len(RecFilename)
    #         FileNames=[]
    #         for i in range(L):
    #             filename,ext=os.path.splitext(RecFilename[i])
    #             filename=LoggerSN[i] + '_' + filename + '.wav'
    #             FileNames.append(os.path.join(Folder, filename))
    #         for file in FileNames:
    #             try:
    #                 os.remove(file)
    #                 print(f"{file} deleted successfully!")
    #             except OSError as error:
    #                 print(error)    
      

    
    # def downloadAudio(self, url):
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         return response.content
    #     else:
    #         return None

    # def playLabel(self):
    #     WavURL=[row[3] for row in self.data]
    #     L=len(WavURL)
    #     for i in range(L):
    #         cell_widget = QWidget()
    #         layout = QVBoxLayout()

    #             # Create play button
    #         play_button = QPushButton("Play")
    #         # play_button.clicked.connect(lambda _, i=i, j=3: self.play_audio(i, 3))
    #         play_button.clicked.connect(lambda:  self.play_audio(WavURL[i], i))

    
    #         # # Create waveform plot
    #         # waveform_plot = WaveformPlot()
    #         # layout.addWidget(waveform_plot)
    #         # self.audio_waveform_plots.append(waveform_plot)    
        
        
    #         # Add play button to layout
    #         layout.addWidget(play_button)
    #         cell_widget.setLayout(layout)
    #         # # Create a QTableWidgetItem and set the custom widget as the cell widget
    #         item = QTableWidgetItem()
    #         item.setFlags(Qt.ItemIsEnabled)  # Make the cell not editable
    #         self.tablewidget.setCellWidget(i, 3 ,cell_widget)
    #         self.tablewidget.setItem(i, 3, item)

    #         # self.tablewidget.setColumnWidth(3, 500)
    #         header = self.tablewidget.horizontalHeader()       
    #         header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

    
    # def download_audio(self, url):
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         # Create a temporary file to save the audio
    #         with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
    #             temp_audio_file.write(response.content)
    #             return temp_audio_file.name
    #     else:
    #         return None
    
    def update_waveform_plot(self):
        # if pygame.mixer.music.get_busy():
        #     audio = pygame.mixer.Sound(self.current_audio_file)
        #     samples = audio.get_raw()
        #     samples = np.frombuffer(samples, dtype=np.int16)

        #     # Update the waveform plot
        #     self.current_waveform_plot.update_plot(samples)

        pass            
    
           
        # ===========================SETTINGS =================================================
 
 
    def specView(self):
        if self.plot_widget.isVisible():
            self.plot_widget.setVisible(False)
            self.spec_view_action.setText("spec view (off)")
            self.text_debug.setFixedHeight(100)
        else:
            self.plot_widget.setVisible(True)
            self.text_debug.setFixedHeight(300) 
            self.spec_view_action.setText("spec view (on)")   
    
    def switchGroup(self, index=0):

        if index==0: # table view    
            train_status=False
            database_status=True
            self.text_debug.setFixedHeight(100)
            self.listRevisit.setVisible(False)

        if index==1:
            self.listRevisit.setVisible(True)
            self.listRevisit.setFixedHeight(100)

        self.middle_layout.setCurrentIndex(index)
        
        # if self.training_view_action.toolTip()=='train':
        #     train_status=True
        #     database_status=False
      
        #     self.text_debug.setFixedHeight(300)

        # else:
        #     train_status=False
        #     database_status=True
        #     self.text_debug.setFixedHeight(100)

            
        # self.listTrain1.setVisible(train_status)
        # self.label_Train1.setVisible(train_status)
        # self.listTrain2.setVisible(train_status)
        # self.label_Train2.setVisible(train_status)
        # self.listTest.setVisible(train_status)
        # self.label_Test.setVisible(train_status)


        # self.radio_button_spec.setVisible(train_status)
        # self.radio_button_audio.setVisible(train_status)
        # self.btn_Play.setVisible(train_status)

        # if index==0 or index==1 :
        #     # self.plot_widget.setVisible(train_status)
        #     pass


        # self.btn_train_model.setVisible(train_status)
        # self.btn_test_model.setVisible(train_status)
        # self.btn_extract_feature.setVisible(train_status)

        
        # self.tablewidget.setVisible(database_status) 
        # self.toolbar.setVisible(database_status)
        # self.table_menu.setEnabled(database_status)
        # self.btn_next_page.setVisible(database_status)
        # self.btn_prev_page.setVisible(database_status)
        # self.btn_all_page.setVisible(database_status)
        # self.btn_ProcessSpecAudio.setVisible(database_status)
        # self.btn_RunModel.setVisible(database_status)

        # if self.training_view_action.toolTip()=='train':
        #     self.training_view_action.setToolTip("database")
        #     self.populateListBox()
        # else:
        #     self.training_view_action.setToolTip('train')

 
   

    # def playWavFile(self):
    #     # file_path = "your_wav_file.wav"  # Replace "your_wav_file.wav" with the path to your WAV file
    #     self.sound_effect.setSource(QUrl.fromLocalFile(self.last_file))
    #     self.sound_effect.play()        

        

    def browseFolder(self, item=None):
        list_widget=self.sender()
        Folder=list_widget.property("Folder")
        if list_widget.currentRow()==0:
            Folder=os.path.dirname(Folder)
            # list_widget.setProperty("Folder", Folder)
            dirStructure(Folder, list_widget)
        else:
            item=os.path.join(Folder, item.text())
            if os.path.isdir(item): #item is a folder
                # list_widget.setProperty("Folder", item)
                dirStructure(item, list_widget)
            else: # item is a file
                os.startfile(item)

      


    def table_selection_changed(self):

        selected_items=self.tablewidget.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            column = selected_items[0].column()
            # print(f"Selected row: {row}, column: {column}")
            item = self.tablewidget.item(row, column)
            if item is not None:
                # print(f"Item at row {row}, column {column}: {item.text()}")
                if column==1:
                    hex_timestamp=item.text().split('.')[0]
                    timestamp = int(hex_timestamp, 16)
                    date_time = datetime.datetime.fromtimestamp(timestamp)
                    formatted_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
                    self.setWindowTitle(item.text() + ', ' + formatted_date_time)
                else:
                    self.setWindowTitle(item.text())
                    if self.plot_widget.isVisible():
                        if self.headers[column]=='LS1_SpecFileURL' or self.headers[column]=='LS1_AudioProfile':
                            # response = requests.get(item.text())
                            # image_data = response.content
                            # self.plot_widget.plot_image(image_url=item.text())
                            QTimer.singleShot(100, lambda: self.plot_widget.plot_image(image_url=item.text()))
                        
                        if self.headers[column]=='LS1_WavFileURL':
                            # play_wav_from_url(item.text())
                              # Start a thread to play audio and plot waveform
                            # self.audio_url=item.text()
                            # self.play_thread = Thread(target=play_audio_from_url, args=(self.audio_url, self.plot_widget))
                            # self.play_thread.start()

                            # audio_player = AudioPlayer(item.text(), self.plot_widget)
                            # audio_thread = Thread(target=audio_player.play_audio)
                            # audio_thread.start()

                            os.startfile(item.text())

                        

                # pyperclip.copy(item.text())
                
            
           
    
    # def show_external_window(self):
    #     # Create a new window for the figure
    #     external_window = QMainWindow()
    #     external_window.setWindowTitle("External Figure")
    #     external_window.setGeometry(200, 200, 600, 400)

    #     # Create the figure widget and add it to the window
    #     figure = plt.figure()
    #     canvas = FigureCanvas(figure)
    #     # toolbar = NavigationToolbar(canvas, external_window)
    #     # external_window.setCentralWidget(canvas)
    #     # external_window.addToolBar(toolbar)

    #     # Create a simple plot
    #     ax = figure.add_subplot(111)
    #     x = np.linspace(0, 10, 100)
    #     y = np.sin(x)
    #     ax.plot(x, y)

    #     # Show the window
    #     external_window.show()        
  
        

    
    
    
        
    def runQuery(self):
        self.clear_table()
        if self.gcp==None:
            self.gcp=gcp()
            
        # sql()
        s, data, headers=self.gcp.makeQuery()
        if s:
            if data:
                self.data=data
                self.headers=headers
                self.populateTable()

       
    # def exportTable(self):
    #     rowCount = self.tablewidget.rowCount()
    #     columnCount = self.tablewidget.columnCount()
    #     # add this line
    #     data = []
    #     data.append(self.headers)
    #     for row in range(rowCount):
    #         rowData = []
    #         for column in range(columnCount):
    #             widgetItem = self.tablewidget.item(row, column)
    #             if widgetItem and widgetItem.text:
    #                 rowData.append(widgetItem.text())
    #             else:
    #                 rowData.append('NULL')
    #         # print(rowData)

    #         # add this line
    #         data.append(rowData)

    #     # change these two lines
    #     df = pd.DataFrame(data)
    #     fn='C:\\WI\\Table.xlsx'
    #     df.to_excel(fn, header=False, index=False)
    #     # os.system("start " + fn)
    #     os.startfile(fn)

    #     # Convert data to JSON
    #     fn_json=fn='C:\\WI\\data.json'
    #     json_data = []
    #     keys = data[0]
    #     for entry in data[1:]:
    #         json_data.append(dict(zip(keys, entry)))

    #     # Write JSON data to a file
    #     with open(fn_json, 'w') as json_file:
    #         json.dump(json_data, json_file, indent=4)
    

                
    # def read(self):
    #     pass
    def read_table(self, selected_item=None, dataset_id='LS1_Data', tablename='LS1_RawWavURL'):
        
        if selected_item is None:

            # items = ["ALL", "Empty,NULL,None", "SpecURL", "None"]
            items = ["Today", "Dates - Test", "Dates - Upload", "Empty URL", "LoggerSN", "Noise NOT null", "Noise types", "ALL"]
            # selected_item=listBox(items, TitleStr="Select an item", width=500, height=300)
            if developer:
                items.insert(0, 'TEST') 
            dialog = SelectDialog(items, 'Select a condition',2)
            
            response=dialog.exec()
            if response:
            # if dialog.exec() == QDialog.Accepted:
                selected_item = dialog.get_selected_item()
                print(f"Selected Item: {selected_item}")
                if selected_item.startswith("Dates"):
                    calendar_dialog = CalendarDialog()
                
                    # Center the calendar dialog on the parent window
                    # parent_rect = self.frameGeometry()
                    # dialog_rect = calendar_dialog.frameGeometry()
                    # dialog_rect.moveCenter(parent_rect.center())
                    # calendar_dialog.move(dialog_rect.topLeft())

                    self.moveToCentre(calendar_dialog)

                    result = calendar_dialog.exec()
                    if result == QDialog.Accepted:
                        if selected_item=="Dates - Test":
                           selected_item ="Date=" + calendar_dialog.get_selected_date()
                        else:
                           selected_item ="UploadDate=" + calendar_dialog.get_selected_date() 
                        
                        print("Selected Date:", selected_item)

                    else:
                        selected_item=None    
                        # selected_item="2023-09-06"
                if selected_item=="Today":
                    current_date= datetime.datetime.now()
                    selected_item = "Date="+current_date.strftime('%Y-%m-%d')

                if selected_item=="TEST":
                    selected_item ='Date=2023-10-30'        

                if selected_item=="LoggerSN":
                    selected_item="LoggerSN=" + singleInput(" ", TitleStr='logger sn')

        if selected_item=='Date':
            if self.start_date.date() == self.end_date.date():
                selected_item = "Date="+self.start_date.date().toString("yyyy-MM-dd")
            else:
                selected_item = "Range="+self.start_date.date().toString("yyyy-MM-dd") + ' to ' + self.end_date.date().toString("yyyy-MM-dd")
        
        if selected_item:
            if self.gcp==None:
                logging.info('initiating gcp')
                self.gcp=gcp()                                
            self.query=[dataset_id, tablename, selected_item]

            self.creat_spec_images=True
            self.clear_all_graphics()
            self.clearTableWidgets()

            # Add the Stop button to the toolbar and store the QAction
            # self.stop_action = self.toolbar.addWidget(self.btn_Stop)
            self.stop_action.setVisible(True)
            QCoreApplication.processEvents()
            
            self.worker = ReadWorker(self.gcp, dataset_id, tablename, selected_item)
            self.worker.resultReady.connect(self.on_data_fetched)  # Handle the result
            self.worker.start()  # Start thread

    def on_data_fetched(self, data, headers, selected_item):
        self.stop_action.setVisible(False)
        """Receive data from the worker thread and update UI."""
        self.data = data
        self.headers = headers
        
        if self.data:
            self.populateTable()
            self.populateHeaders()
            self.Data=self.data
        else:
            # self.updateLogBox(f"no data found for {selected_item}!" )
            logging.info(f"no data found for {selected_item}!")
            msgBox(f"no data found for {selected_item}!", "no data" )
    
    def populateHeaders(self):
        # self.LoggerSN= [row[0] for row in self.data]
        self.LoggerSN= [row[self.headers.index('LS1_LoggerSN')] for row in self.data]
        # self.RecFilename= [row[1] for row in self.data]
        self.RecFilename= [row[self.headers.index('LS1_RecFilename')] for row in self.data]
        
        # self.WavFileURL=[row[3] for row in self.data]
        self.WavFileURL=[row[self.headers.index('LS1_WavFileURL')] for row in self.data]
        
        # self.SpecFileURL= [row[7] for row in self.data]
        self.SpecFileURL= [row[self.headers.index('LS1_SpecFileURL')] for row in self.data]
        Audio_col_id=self.headers.index('LS1_AudioProfile')
        # self.AudioProfile=[row[10] for row in self.data]
        self.AudioProfile=[row[self.headers.index('LS1_AudioProfile')] for row in self.data]

        self.LS1Auto=[row[self.headers.index('LS1_Auto')] for row in self.data] 
     
        self.filtered_headers=[]
        # if self.data:
        #     self.populateTable()
        # else:
        #     # self.updateLogBox(f"no data found for {selected_item}!" )
        #     logging.info(f"no data found for {selected_item}!")
        #     msgBox(f"no data found for {selected_item}!", "no data" )
            
    
    def moveToCentre(self, child_widget):
        parent_rect = self.frameGeometry()
        dialog_rect = child_widget.frameGeometry()
        dialog_rect.moveCenter(parent_rect.center())
        child_widget.move(dialog_rect.topLeft())
        


    def reloadTable(self):
        self.clear_table()
        [self.data,self.headers]=self.gcp.read(self.query[0], self.query[1], self.query[2]) 
        self.filtered_headers=[]
        if self.data:
            self.populateTable()
        else:
            msgBox(f"no data found for {self.query[2]}!", "no data" )                    
    
    def populateTable(self):
    # def populateTable(self, data, headers):
        self.switchGroup(index=0)
        if not self.data:
            logging.info(f"hit SEARCH button from toolbar")
            return
            
       
        # self.clear_table()
        self.clearTableWidgets()
        # if self.settings['current_page']:
        #     start_row = (self.settings['current_page'] - 1) * self.settings['items_per_page']
        #     end_row = min(start_row + self.settings['items_per_page'], len(self.data))
        #     if start_row>end_row:
        #         start_row=0
        #         end_row = min(start_row + self.settings['items_per_page'], len(self.data))
        #         self.settings['current_page']=1
        #     if start_row<0:
        #         self.settings['current_page']=math.ceil(len(self.data)/ self.settings['items_per_page'])
        #         start_row = (self.settings['current_page'] - 1) * self.settings['items_per_page']
        #         end_row=len(self.data)    
        # else:
        #     start_row=0
        #     end_row=len(self.data)
        start_row=0
        end_row=len(self.data)
         
        # if data is None:
        #     data=self.data
        self.TableData=self.data[start_row: end_row][:]
        # self.TableHeader=self.headers
        # rowCount = self.tablewidget.rowCount()
        # numrows = len(self.TableData)  # no of rows
        self.setWindowTitle(f"total entry :  {len(self.data)}")
             
        # numcols = len(self.TableData[0])# no of columns
        # if len(self.TableHeader)==numcols:
        #     Columns=range(numcols)
        # else:
        #     Columns=[]
        #     for str_header in self.TableHeader:
        #         Columns.append(self.TableHeader.index(str_header))
        #     numcols=len(Columns)

        num_rows = end_row - start_row
        self.tablewidget.setRowCount(num_rows)

        # self.tablewidget.setRowCount(numrows)
        self.tablewidget.setRowCount(num_rows) 
        # self.tablewidget.setColumnCount(numcols)
        self.tablewidget.setColumnCount(len(self.data[0]))
        self.tablewidget.setHorizontalHeaderLabels(self.headers)
        self.tablewidget.setVerticalHeaderLabels([str(start_row + i + 1) for i in range(num_rows)])

        for row in range(start_row, end_row):
            for col in range(len(self.data[row])):
                temp=self.data[row][col]
                if isinstance(temp, datetime.datetime):
                    temp = temp.strftime("%Y-%m-%d %H:%M:%S")
                item = QTableWidgetItem(temp)
                self.tablewidget.setItem(row - start_row, col, item)

                # item_width = item.sizeHint().width()
                # if self.tablewidget.columnWidth(col) < item_width:
                #     self.tablewidget.setColumnWidth(col, item_width)

        


    
    def updateCell(self, row_id, fieldname, value=None, colour=None):
        col_id=self.headers.index(fieldname)
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        
        # self.tablewidget.item(row_id, col_id).setText(value)
        item = self.tablewidget.item(row_id, col_id)
        if value:
            item.setText(value)
        if colour:
            # item.setForeground(QColor(255, 0, 0))
            item.setBackground(QColor(255, 0, 0)) 
    
    def clearCell(self, row_id):
        column_count = self.tablewidget.columnCount()
        for column in range(column_count):
            item = self.tablewidget.item(row_id, column)
            if item is not None:
                item.setText("")               
    
    def clearTableWidgets(self):
        for row in range(self.tablewidget.rowCount()):
            for col in range(self.tablewidget.columnCount()):
                item = self.tablewidget.item(row, col)
                if item is not None:
                    self.tablewidget.removeCellWidget(row, col)
                    self.tablewidget.setItem(row, col, None)
    
    def nextPage(self):
        self.settings['current_page']=self.settings['current_page']+1
        self.populateTable()

    def prevPage(self):
        self.settings['current_page']=self.settings['current_page']-1
        self.populateTable()
    
    def allPage(self):
        self.settings['current_page']=[]
        self.populateTable()
               
    
    def clear_table(self):
        self.tablewidget.clearContents()
        self.tablewidget.setRowCount(0)
    def exportFileName(self):
        LoggerSN= [row[0] for row in self.TableData]
        RecFilename= [row[1] for row in self.TableData]
        L=len(RecFilename)
        FileNames=[]
        for i in range(L):
            filename,ext=os.path.splitext(RecFilename[i])
            filename=LoggerSN[i] + '_' + filename + '.wav'
            FileNames.append(os.path.join(Folder, filename))

        
        with open('C:\\WI\\new_files.json', 'w', encoding='utf-8') as f:
            json.dump(FileNames, f, ensure_ascii=False, indent=4)

    def load(self):

        # self.data = []
        # # Open the file and read the content in a list
        # with open('data.txt', 'r') as filehandle:
        #     for line in filehandle:
        #         # Remove linebreak which is the last character of the string
        #         curr_place = line[:-1]
        #         # Add item to the list
        #         self.data.append(curr_place)
        
        # self.headers=[]
        # with open('header.txt', 'r') as filehandle:
        #     for line in filehandle:
        #         # Remove linebreak which is the last character of the string
        #         curr_place = line[:-1]
        #         # Add item to the list
        #         self.headers.append(curr_place)

        with open(self.fsave, "rb") as file:
            data = pickle.load(file)
        self.data=data['data']
        self.headers=data['headers']        

        self.current_page=1        
        self.populateTable()

    # def save(self):
     
    #     # with open('data.txt', 'w') as filehandle:
    #     #     for listitem in self.data:
    #     #         filehandle.write(f'{listitem}\n')

    #     # with open('header.txt', 'w') as filehandle:
    #     #     for listitem in self.headers:
    #     #         filehandle.write(f'{listitem}\n')

    #     # Save the lists to a file using pickle
    #     with open(self.fsave, "wb") as file:
    #         pickle.dump({"data": self.data, "headers": self.headers}, file)        
        
    # def radio_button_toggled(self):
    #     sender = self.sender()  # Get the radio button that triggered the signal
    #     if sender.isChecked():
    #         # print(f"Selected option: {sender.text()}")
    #         self.processFile(item=None)


        

    def renameFiles(self):
        number_of_items = self.list_widget.count()

        items_list = [self.list_widget.item(index).text() for index in range(self.list_widget.count())]

        for i in range(number_of_items):
            print(f"doing {i} of {len(items_list)}")
            current_file=os.path.join(self.list_widget.property("Folder"), self.list_widget.item(i).text())
            current_file_name=os.path.basename(current_file)
            if '_alt=media' in current_file_name:
                new_file_name = current_file_name.split('_alt')[0]
                current_file=os.path.join(self.list_widget.property("Folder"), current_file_name)
                new_file=os.path.join(self.list_widget.property("Folder"), new_file_name)
                os.rename(current_file, new_file)
                items_list[i] = new_file_name

                          
        
        self.list_widget.clear()
        self.list_widget.addItems(items_list)   

    def on_date_changed(self, date):
        self.end_date.setDate(date)

    def quit(self):
        # save settings
        self.app.quit()

    def create_menu(self): 

        # ======================  MENUBAR and MENUS  ==============================
        self.menu_bar=self.menuBar()
        
        # FILE menu
        self.menu_file=self.menu_bar.addMenu("📋Job list")
        self.menu_file.setEnabled(False)
        # self.file_menu.setVisible(False)

        open_file_action=self.menu_file.addAction("Open 📂")
        open_file_action.triggered.connect(self.open_revisit_list)
        save_file_action=self.menu_file.addAction("Save 💾")
        save_file_action.triggered.connect(self.save_revisit_list)

        clear_joblist_action=self.menu_file.addAction("Clear 🧹")
        clear_joblist_action.triggered.connect(self.clear_job_list)
        
        export_joblist_action=self.menu_file.addAction("Export  📤")
        export_joblist_action.triggered.connect(self.exportJobList)
          
        quit_action=self.menu_file.addAction("Quit 🚪🚶‍♂️")
        quit_action.triggered.connect(self.quit) 

        # Help menu
        self.menu_help=self.menu_bar.addMenu("❓Help")
        self.menu_help.setEnabled(False)
        self.stop_action=self.menu_help.addAction("stop ❌")
        self.stop_action.setVisible(False)
        self.stop_action.triggered.connect(self.stop_populating_images)
        about_action=self.menu_help.addAction("about 📝")
        about_action.triggered.connect(self.about)
        update_action=self.menu_help.addAction("check update 🔄")
        update_action.setEnabled(False)
        # update_action.triggered.connect(lambda : self.check_update.check_for_new_version())
        # update_action.triggered.connect(self.checkUpdate)
        
        if developer:
            test_a_function_action=self.menu_help.addAction("test a function")
            test_a_function_action.triggered.connect(self.test_a_function)

         # login menu
        self.menu_login=self.menu_bar.addMenu("🤔User")
        self.login_action=self.menu_login.addAction('log in 🔑 ')
        self.login_action.triggered.connect(self.show_login_dialog)
        self.logout_action=self.menu_login.addAction("log out 🏃‍♂️")
        self.logout_action.setVisible(False)
        self.logout_action.triggered.connect(lambda: self.enable_widgets(status=False))

        self.register_action=self.menu_login.addAction('register  ✍️')
        self.register_action.triggered.connect(self.show_register_dialog)
        


        # self.menu_admin=self.menu_bar.addMenu("Admin")
        # self.licence_table_action=self.menu_admin.addAction('licence table')
        # self.menu_bar.removeAction(self.menu_admin.menuAction()) # hide admin initially

        

         
    def create_toolbar(self):
        #==========================TOOLBARS=============================
        self.toolbar=QToolBar("toolbar")
        self.toolbar.setIconSize(QSize(16,16))
        # self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        self.addToolBar(self.toolbar)


        # Create a spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

       
        # Create a QDateEdit field with a calendar popup
        self.start_date = QDateEdit(self)
        self.start_date.setEnabled(False)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        # Connect date change event
        self.start_date.dateChanged.connect(self.on_date_changed)
        # Add QDateEdit to toolbar
        self.toolbar.addWidget(self.start_date)
        self.toolbar.addSeparator()

        self.toolbar.addWidget(QLabel(" to ", self))
        self.toolbar.addSeparator() 

        # Create a QDateEdit field with a calendar popup
        self.end_date = QDateEdit(self)
        self.end_date.setEnabled(False)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        # Add QDateEdit to toolbar
        self.toolbar.addWidget(self.end_date)
        self.toolbar.addSeparator()

        # Button 
        self.btn_Search=QPushButton("🔍Search")
        self.btn_Search.setEnabled(False)
        # self.btn_Connect.setGraphicsEffect(shadow_effect)
        self.btn_Search.clicked.connect(lambda : self.read_table(selected_item="Date"))
        self.btn_Search.setVisible(True)
        # self.btn_Download.setMinimumWidth(150)
        self.toolbar.addWidget(self.btn_Search)
        self.toolbar.addSeparator()

        self.reload_action=QAction(QIcon(refresh_icon_file), "reload table", self)
        self.reload_action.setEnabled(False)
        # reload_action=QPushButton("🔄")
        self.reload_action.setStatusTip("reload table")
        self.reload_action.triggered.connect(self.reloadTable)
        # reload_action.clicked.connect(self.reloadTable)
        self.toolbar.addAction(self.reload_action)
        # self.toolbar.addWidget(reload_action)
        self.toolbar.addSeparator()
       

        # self.toolbar.addWidget(spacer)
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(500)
        self.progress_bar.setValue(0)
        self.toolbar.addWidget(self.progress_bar)
        self.toolbar.addSeparator()
           

          
    
        # Add it to the toolbar
        # self.toolbar.addWidget(spacer)


        self.btn_TableView=QPushButton("📋Table")
        self.btn_TableView.setEnabled(False)
        # self.btn_TableView.clicked.connect(lambda : self.switchGroup(index=0))
        self.btn_TableView.clicked.connect(self.populateTable)
        
        # self.btn_TableView.setVisible(True)
        self.toolbar.addWidget(self.btn_TableView)
        self.toolbar.addSeparator()
        
        self.btn_GridView=QPushButton("📊Grid")
        self.btn_GridView.setEnabled(False)
        # self.btn_GridView.clicked.connect(self.populateSpecImages)
        self.btn_GridView.clicked.connect(self.start_populating_images)
        self.toolbar.addWidget(self.btn_GridView)
        self.toolbar.addSeparator()
        
        # Create the stop button widget but do not add it to toolbar yet, add before running a thread
        # and remove it after the thread finishes
        # self.btn_Stop=QPushButton("🛑Stop")
        # self.btn_Stop.clicked.connect(self.stop_populating_images)
        # self.btn_Stop.setEnabled(False)
        # self.btn_Stop.setVisible(False)
        # self.toolbar.addWidget(self.btn_Stop)
        # self.toolbar.addSeparator()



    def create_widgets(self):
           
        #==================================listbox===================================
        self.label_Train1 = QLabel("<b>TRAIN SET 1</b>")
        self.label_Train1.setAlignment(Qt.AlignCenter)
        # self.label_Train1.setVisible(False)
        self.listTrain1 = QListWidget()
        self.listTrain1.setToolTip("left train list")
        self.listTrain1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listTrain1.customContextMenuRequested.connect(self.menu_listbox)
        # self.listTrain1=ListWidget()
        self.listTrain1.maximumWidth=50
        # self.listTrain1.resize(150,300)
        # self.listTrain1.addItem("..")
        # self.listTrain1.setSizeAdjustPolicy(self.listTrain1.adjustSize)
        # self.listTrain1.currentItemChanged.connect(self.browseFolder)
        # self.listTrain1.itemClicked.connect(self.processFile)
        self.listTrain1.itemDoubleClicked.connect(self.browseFolder)
        # self.listTrain1.setProperty("Folder", self.settings['TrainFolder1'])
        # self.listTrain1.setVisible(False)
        
        
        self.label_Train2 = QLabel("<b>TRAIN SET 2</b>")
        self.label_Train2.setAlignment(Qt.AlignCenter)
        # self.label_Train2.setVisible(False)
        self.listTrain2 = QListWidget()
        self.listTrain2.setToolTip("middle train list")
        self.listTrain2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listTrain2.customContextMenuRequested.connect(self.menu_listbox)
        self.listTrain2.maximumWidth=50
        # self.listTrain2.itemClicked.connect(self.processFile)
        self.listTrain2.itemDoubleClicked.connect(self.browseFolder)
        # self.listTrain2.setProperty("Folder", self.settings['TrainFolder2'])
        # self.listTrain2.setVisible(False)

        self.label_Test = QLabel("<b>TEST</b>")
        self.label_Test.setAlignment(Qt.AlignCenter)
        # self.label_Test.setVisible(False)
        self.listTest = QListWidget()
        self.listTest.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listTest.customContextMenuRequested.connect(self.menu_listbox)
        self.listTest.setToolTip("right TEST list")
        self.listTest.maximumWidth=50
        # self.listTest.itemClicked.connect(self.processFile)
        self.listTest.itemDoubleClicked.connect(self.browseFolder)
        # self.listTest.setProperty("Folder", self.settings['TestFolder'])
        # self.listTest.setVisible(False)

        self.listResult = QListWidget()
        self.listResult.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listResult.setToolTip("reuslt list")
        self.listResult.maximumWidth=50
        # self.listResult.setVisible(False) 

        # self.plot_widget=PlotWidget(self)
        # self.plot_widget.setVisible(False)


        # Create radio buttons and add them to the layout
        # self.radio_button_spec = QRadioButton("spec")
        # self.radio_button_spec.setChecked(True)
        # # self.radio_button_spec.toggled.connect(self.radio_button_toggled)
        # self.radio_button_spec.setVisible(False)
        # self.radio_button_audio = QRadioButton("audio")
        # self.radio_button_audio.toggled.connect(self.radio_button_toggled)
        # self.radio_button_audio.setVisible(False)
        

        # ============================text box================================= 
        # self.text_box = QLabel()
        self.text_box = QTextEdit()
        # self.text_box.setGeometry(50, 50, 200, 100)  # set the position and size of the widget
        self.text_box.setVisible(False)
        self.text_box.setPlainText("Model output")  # set the default text
        # self.text_box.setText("Model output")  # set the default text

        # self.text_search = QTextEdit()
        # self.text_search.setFixedSize(500, 30)
        # self.text_search.setReadOnly(False)
        # self.text_search.setVisible(False)
        # self.text_search.setLineWrapMode(QTextEdit.NoWrap)
        # self.text_search.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.text_search.keyPressEvent = self.keyPressEvent
           
        #===================================table widget========================================
        self.tablewidget=QTableWidget()
        self.tablewidget.itemSelectionChanged.connect(self.table_selection_changed)
        self.tablewidget.setAlternatingRowColors(True)
        self.tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tablewidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
  
        
        # self.context_menu = QMenu()
        # self.open_action = QAction("open", self)
        # self.context_menu.addAction(self.open_action)
        # self.find_action = QAction("find", self)
        
        # self.context_menu.addAction(self.find_action)
        self.tablewidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tablewidget.customContextMenuRequested.connect(self.handleContextMenu)
        header = self.tablewidget.horizontalHeader()
        header.sectionClicked.connect(self.on_header_clicked)
        # self.open_action.triggered.connect(self.openItem)
        # self.find_action.triggered.connect(self.findItem)


        

        #================================ FIGURE ==============================  
        # self.figure=Figure()
        # self.figure=plt.figure()
        # self.canvas=FigureCanvas(self.figure)

        # self.graphWidget = pg.PlotWidget()
        # self.graphWidget.setMinimumWidth(500)
        # self.graphWidget.setMaximumWidth(800)
        
        
        # ax = fig.add_subplot(111)
        # ax.plot([1, 2, 3, 4, 5], [10, 20, 30, 40, 50])



        # =================================buttons======================================
        # self.btn_train_model=QPushButton("TRAIN")
        # # self.btn_train_model.setStyleSheet("background-color: 	#c0c0c0")
        # self.btn_train_model.setVisible(False)
        # # self.btn_Download.setMaximumWidth(150)
        # # QFont.setWeight(QFont.bold)
        # self.btn_train_model.setFont(QFont('Times',14))
        # self.btn_train_model.clicked.connect(lambda : self.runModelProcessor(train_model=True))

        # self.btn_test_model=QPushButton("TEST")
        # self.btn_test_model.setVisible(False)
        # self.btn_test_model.setFont(QFont('Times',14))
        # self.btn_test_model.clicked.connect(lambda : self.runModelProcessor(test_model=True))

        # self.btn_extract_feature=QPushButton("EXTRACT FEATURES")
        # self.btn_extract_feature.setVisible(False)
        # self.btn_extract_feature.setFont(QFont('Times',14))
        # self.btn_extract_feature.clicked.connect(lambda : self.runModelProcessor(extract_feature=True))

        # self.btn_next_page=QPushButton("Next Page")
        # self.btn_next_page.setFont(QFont('Times',14))
        # self.btn_next_page.clicked.connect(self.nextPage)
        
        # self.btn_prev_page=QPushButton("Prev Page")
        # self.btn_prev_page.setFont(QFont('Times',14))
        # # self.btn_Exit.clicked.connect(self.quit)
        # self.btn_prev_page.clicked.connect(self.prevPage)

        # self.btn_all_page=QPushButton("ALL")
        # self.btn_all_page.setFont(QFont('Times',14))
        # self.btn_all_page.clicked.connect(self.allPage)

        # self.btn_ProcessSpecAudio=QPushButton("Process Spec/Audio")
        # # self.btn_ProcessSpecAudio.clicked.connect(self.runSpecAudioProcessor)
        # self.btn_ProcessSpecAudio.setFont(QFont('Times',14))
        

        # # self.worker=None
        # self.btn_RunModel=QPushButton("Run Model")
        # self.btn_RunModel.setFont(QFont('Times',14))
        # # self.btn_RunModel.clicked.connect(self.start_worker)
        # self.btn_RunModel.clicked.connect(lambda : self.runModelProcessor(test_model=True))

        
        # self.btn_SearchFromDatabase=QPushButton("SEARCH")
        # self.btn_SearchFromDatabase.setFont(QFont('Times',14))
        # self.btn_SearchFromDatabase.clicked.connect(self.readFromDatabase)
        
  

        # self.btn_Play=QPushButton("Play")
        # self.btn_Play.setFont(QFont('Times',14))
        # # self.btn_Play.clicked.connect(self.playWavFile)
        # self.btn_Play.setVisible(False)


        # debug and update box
        self.text_debug=QTextEdit(self)
        self.text_debug.setReadOnly(True)
        self.text_debug.setFixedHeight(100)
        # self.text_debug.setFixedWidth(400) 
        
        
        self.listRevisit = QListWidget()
        # self.listResult.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listRevisit.setToolTip("revisit site")
        # self.listResult.maximumWidth=50
        self.listRevisit.setVisible(False)
        
        # Set up the logging configuration
        # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        # # Create a QtHandler and attach it to the root logger
        # qt_handler = QtHandler(self.text_debug)
        # logging.getLogger().addHandler(qt_handler)

        


    
    def create_layout(self): # layout

        w = QWidget()
        self.setCentralWidget(w)

        # self.grid_layout = QGridLayout()
    
        top_layout=QHBoxLayout()
        top_layout.addWidget(self.text_debug)
        # top_layout.addWidget(self.plot_widget)
        top_layout.addWidget(self.listRevisit)

        # Create the scrollable middle layout for the groups
        self.middle_container = QScrollArea()
        self.middle_container.setWidgetResizable(True)

        # Container for the dynamic plot layout
        self.group_spec = QWidget()
        self.plot_layout = QGridLayout()  # Initialize the grid layout
        self.group_spec.setLayout(self.plot_layout)
        self.middle_container.setWidget(self.group_spec)
        
        self.group_train=QWidget()
        self.group_table=QWidget()
        
        # Initialize the QStackedLayout to hold multiple views
        self.middle_layout = QStackedLayout()
        self.middle_layout.addWidget(self.group_table)  # Existing table view
        # self.middle_layout.addWidget(self.group_train)  # Existing training view, Commenting/removing this line doen't let to create spec view images, need to find out why?
        self.middle_layout.addWidget(self.middle_container)  # Scrollable group_spec view

        self.middle_layout.setCurrentIndex(0)  # Default to the first group


        # Create a container for the middle layout
        middlebox = QGroupBox("")
        middlebox.setLayout(self.middle_layout)
        
        

        # Create layout widgets for group1
        # train_layout=QHBoxLayout(self.group_train)
        
        # train1_column = QVBoxLayout()
        # train1_column.addWidget(self.label_Train1)
        # train1_column.addWidget(self.listTrain1)
        # train_layout.addLayout(train1_column)

        # train2_column = QVBoxLayout()
        # train2_column.addWidget(self.label_Train2)
        # train2_column.addWidget(self.listTrain2)
        # train_layout.addLayout(train2_column)

        # test_column = QVBoxLayout()
        # test_column.addWidget(self.label_Test)
        # test_column.addWidget(self.listTest)
        # train_layout.addLayout(test_column)

        # Group 2
        group2_layout=QHBoxLayout(self.group_table)
        group2_layout.addWidget(self.tablewidget)

       
         
        # Create a layout for the widget
        # self.radio_layout = QHBoxLayout()
        # self.radio_layout.addWidget(self.radio_button_spec)
        # self.radio_layout.addWidget(self.radio_button_audio)
           
        

        # bottomlayout=QHBoxLayout()
        # bottomlayout.addWidget(self.btn_next_page)
        # bottomlayout.addWidget(self.btn_prev_page)
        # bottomlayout.addWidget(self.btn_all_page)

        # if developer:
        #     bottomlayout.addWidget(self.btn_train_model)
        #     bottomlayout.addWidget(self.btn_test_model)
        #     bottomlayout.addWidget(self.btn_extract_feature)

        #     # bottomlayout.addWidget(self.text_search)
        #     bottomlayout.addWidget(self.btn_RunModel)

        # bottomlayout.addWidget(self.btn_SpecView)
        # bottomlayout.addWidget(self.btn_ProcessSpecAudio)

        # bottomlayout.addLayout(self.radio_layout)
        # bottomlayout.addWidget(self.btn_Play)

        main_layout=QVBoxLayout(w)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(middlebox)
        # main_layout.addLayout(bottomlayout)
        
        # spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # main_layout.addItem(spacer)
        self.setLayout(main_layout)


        # if self.settings['ViewType'] !='table':
        #     self.changeView()

    
    # def checkUpdate(self):

       
    #     self.check_update=updateApp(current_version=version_no,url_version=version_url,running_app= app_exe_path)
    #     self.check_update.finished.connect(self.processUpdate)
    #     self.check_update.start()
    #     self.animate_bar=animateProgressBar(self.progress_bar)
    #     self.animate_bar.start()
                

    def about(self):
        self.setWindowTitle(f"version no : {version_no}, release : {release_date}")
        # self.setWindowTitle(self.check_update.running_app)
        # self.animation_widget.stop_animation()


    @Slot()
    def exit_app(self):
        """Exit application and stop thread"""
        self.stop_thread()
        self.tray_icon.hide()
        QApplication.quit()        
    
    def load_stylesheet(self, filename):
        """Loads and applies the QSS stylesheet from the specified file."""
        file = QFile(filename)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            self.setStyleSheet(stylesheet)
        else:
            print(f"Failed to load stylesheet from {filename}")
  

def main(): 
    
    import sys
    app=QApplication(sys.argv)
    # Load the QSS theme
    # with open("styles.qss", "r", encoding="utf-8") as f:
    #     app.setStyleSheet(f.read())

    with open(style_file, 'r', encoding="utf-8") as f:
        stylesheet = f.read()
    app.setStyleSheet(stylesheet)

    # QApplication.instance().setStyleSheet(stylesheet)
    
    # file = QFile(f"styles.qss")
    # if file.open(QFile.ReadOnly | QFile.Text):
    #     stream = QTextStream(file)
    #     stylesheet = stream.readAll()
    #     QApplication.instance().setStyleSheet(stylesheet)

      

    app.setWindowIcon(QIcon(icon_file))
  
    # app.setQuitOnLastWindowClosed(False)  # Keep app running in tray
    window=mainUI(app)
    window.show()# by default window is hidden, so needs to be shown

    
    if getattr(sys, 'frozen', False):
        pyi_splash.close()
        # log.info('Splash screen closed.')
    
    
    # Bring the window to the front when the application starts
    # window.raise_()
    # window.activateWindow() 
    # app.exec()  

    sys.exit(app.exec())


if __name__=="__main__":
    main()    