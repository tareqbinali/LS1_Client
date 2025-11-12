#  last update 09 Mar 2025
# working fine so far.

# import PyInstaller.__main__
# from PyInstaller.utils.hooks import get_package_paths


from PySide6.QtWidgets import QInputDialog, QApplication
from PySide6.QtGui import QPixmap, QIcon
import subprocess
import os
import re
import sys
from datetime import datetime

from constants import app_name, version_no, release_date

build_path='C:/build_temp'
work_path=os.path.join(build_path, 'pyinstaller_build')
dist_path=os.path.join(build_path, 'pyinstaller_dist')

# Get current timestamp in a readable format
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# Define the output log file with timestamp
log_file = os.path.join(build_path, f'{timestamp}_pyinstaller_build_log.txt')




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

def update_version_file(file_path, current_version, new_version, current_release_date):
    with open(file_path, 'r') as file:
        file_content = file.read()
        # updated_content = re.sub(r'version_no=\d+\.\d+', f'version_no={new_version}', file_content)

        updated_content = file_content.replace(
            f"version_no='{current_version}'", f"version_no='{new_version}'"
        )
        
        # Update release_date with the current date
        # current_release_date = file_content.split("release_date='")[1].split("'")[0]
        new_release_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_content = updated_content.replace(
            f"release_date='{current_release_date}'", f"release_date='{new_release_date}'"
        )
    
    
    with open(file_path, 'w') as file:
        file.write(updated_content)


# current_version = read_version_no()
current_version=float(version_no.strip()) 

user_input, ok_pressed = QInputDialog.getText(
    None,
    "version no",
    f"Enter new number (current is {current_version}):",
    text=str(round(current_version+0.1,1))
)

if ok_pressed:
    # new_version=float(user_input.strip())
    new_version=user_input.strip()

    update_version_file(version_file, version_no,new_version, release_date)


    command=[
        "pyinstaller",
        "main.py",
        '--name', f"{app_name}_{new_version}",
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--icon',
        "logo.ico",
        '--splash',
        "splash.png",
        '--add-data',
        "ls1-sample.json;.",
        '--add-data',"client-cert.pem;.",
        '--add-data',"client-key.pem;.",
        '--add-data',"icon.png;.",
        '--add-data',"styles.qss;.",
        '--add-data',"refresh.png;.",
        '--clean',
        '--debug', 'all',  # Enable debug mode
        '--workpath', work_path,
        '--distpath', dist_path,
    ]

    # Open the log file in write mode
    with open(log_file, 'w') as log:
        # Run PyInstaller command and redirect stdout and stderr to the log file
        process = subprocess.Popen(command, stdout=log, stderr=log)

        # Wait for the process to complete
        process.communicate()

    print(f"PyInstaller build complete. Debug log saved to {log_file}")

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