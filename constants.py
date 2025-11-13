# last update 13 Nov 2025

import os
import sys

version_no = '1.2'
version_url = 'https://drive.google.com/uc?id=1_2T5R9TCR4qZLTGXw5ifjEsBqWlLhAEz'
app_name = 'ls1Client'
release_date = '2025-11-13 14:49:39'


def resource_path(*relative_parts: str) -> str:
    """
    Get absolute path to a resource, working in:
      - normal Python run
      - PyInstaller frozen EXE (onefile / onefolder)
    """
    if getattr(sys, "frozen", False):  # Running from PyInstaller bundle
        base_path = sys._MEIPASS      # type: ignore[attr-defined]
    else:
        # Use the folder where this file lives, not cwd
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, *relative_parts)


# Path to the running script / EXE (useful for updater, etc.)
app_exe_path = os.path.abspath(sys.argv[0])
app_location = os.path.dirname(app_exe_path)

# ---------- Resources bundled with PyInstaller ----------

# Icons / styles that live at bundle root
icon_file = resource_path("icon.png")
style_file = resource_path("styles.qss")
refresh_icon_file = resource_path("refresh.png")

# .secrets folder and files
secret_location   = resource_path(".secrets")
client_cert_file  = resource_path(".secrets", "client-cert.pem")
client_key_file   = resource_path(".secrets", "client-key.pem")
service_file      = resource_path(".secrets", "ls1-sample.json")
