#  last update 03 Mar 2025

import PyInstaller.__main__
from PyInstaller.utils.hooks import get_package_paths


from PySide6.QtWidgets import QInputDialog, QApplication
from PySide6.QtGui import QPixmap, QIcon
import os
import re
import sys
from datetime import datetime

from constants import app_name, version_no, release_date
version_file="constants.py"


app=QApplication(sys.argv) 
# Set the application icon
app.setWindowIcon(QIcon("icon.png"))  
        
def read_version_no(file_path=version_file):
    with open(file_path, 'r') as file:
        content = file.read()
        match = re.search(r'version_no=(\d+\.\d+)', content)
        if match:
            return float(match.group(1))
    return None

def update_version_file(file_path, new_version, current_release_date):
    with open(file_path, 'r') as file:
        file_content = file.read()
        updated_content = re.sub(r'version_no=\d+\.\d+', f'version_no={new_version}', file_content)
        
        # Update release_date with the current date
        # current_release_date = file_content.split("release_date='")[1].split("'")[0]
        new_release_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_content = file_content.replace(
            f"release_date='{current_release_date}'", f"release_date='{new_release_date}'"
        )
    
    
    with open(file_path, 'w') as file:
        file.write(updated_content)


# current_version = read_version_no()
current_version=version_no

user_input, ok_pressed = QInputDialog.getText(
    None,
    "version no",
    f"Enter new number (current is {current_version}):",
    text=str(round(current_version+0.1,1))
)

if ok_pressed:
    new_version=float(user_input.strip())

    update_version_file(version_file, new_version, release_date)


    PyInstaller.__main__.run([
        "main.py",
        '--name', app_name,
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--icon',
        "logo.ico",
        '--splash',
        "splash_tiger.jpg",
        '--add-data',
        "ls1-sample.json;.",
        '--add-data',"client-cert.pem;.",
        '--add-data',"client-key.pem;.",
        '--add-data',"icon.png;.",
        '--add-data',"styles.qss;.",
        '--workpath', 'C:/build_temp/pyinstaller_build',
        '--distpath', 'C:/build_temp/pyinstaller_dist',
        '--clean',
        '--debug', 'all',  # Enable debug mode
    ])

a=1



# PyInstaller.__main__.run([
#     "gcpUI.py",
#     '--noconfirm',
#     '--onedir',
#     '--windowed',
#     '--icon',
#     "logo.ico",
#     '--splash',
#      "splash_tiger.jpg",
#     '--add-data',
#     "ls1-sample.json;.",
#     '--add-data',
#     "icon.png;."
 
# ])



#  '--splash',
    #  "splash_tiger.jpg",


# # the following works but on the way I wanted
# PyInstaller.__main__.run([
#     "gcpUI.py",
#     '--onedir',
#     '--windowed',
#     '--icon',
#     "logo.ico",
#     '--add-data',
#     "ls1-sample.json:_internal/ls1-sample.json",
#     '--add-data',
#     "icon.png:_internal/icon.png."
  
# ])













# The following two functions work
# pyinstaller --noconfirm --onedir --console --icon "C:/Dropbox/PythonProject/GCPClient/logo.ico"  "C:/Dropbox/PythonProject/GCPClient/gcpUI.py"
# pyinstaller --noconfirm --onedir --windowed --icon "C:/Dropbox/PythonProject/GCPClient/logo.ico"  "C:/Dropbox/PythonProject/GCPClient/gcpUI.py"



# auto_py_to_exe location
# C:\Users\tareq\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts

# '--onefile' or '--onedir'
# '--console' or '--windowed'
    # '--distpath',
    # 'C://Output'  # Specify the desired output directory