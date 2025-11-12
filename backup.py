#  still working on it
import subprocess
import os
from datetime import datetime


# Define the target base directory and log directory
TARGET_BASE = r"W:\My Drive\PythonProjectBackup"
LOGDIR = r"C:\Wi"

# Get the directory where the script is located
SOURCE = os.path.dirname(os.path.abspath(__file__))

# Extract the source directory name (e.g., "PythonProject" from "C:\PythonProject")
SOURCE_NAME = os.path.basename(SOURCE)

# Define the target directory by appending the source directory name to the target base
TARGET = os.path.join(TARGET_BASE, SOURCE_NAME)

# Get the current date and time in a consistent format
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create the full log filename
LOGFILE = os.path.join(LOGDIR, f"{current_time}_sync_log_{SOURCE_NAME}.txt")
TEMPLOGFILE = os.path.join(LOGDIR, "temp_log.txt")

# Run robocopy with logging
robocopy_command = [
    "robocopy", SOURCE, TARGET, "/MIR", f"/LOG:{TEMPLOGFILE}", "/TEE", "/NP"
]
subprocess.run(robocopy_command, check=True)


# Filter the temp log file for updated files and append to the main log file
with open(TEMPLOGFILE, "r") as temp_log, open(LOGFILE, "a") as main_log:
    for line in temp_log:
        if "new" in line.lower() or "updated" in line.lower():
            main_log.write(line)

# Clean up the temporary log file
os.remove(TEMPLOGFILE)

print(f"Backup and logging completed successfully. Log file: {LOGFILE}")