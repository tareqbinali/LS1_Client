import sys, os
version_no='1.1'
version_url='https://drive.google.com/uc?id=1_2T5R9TCR4qZLTGXw5ifjEsBqWlLhAEz'
app_name='ls1Client'
release_date='2025-03-19 06:01:58'

app_exe_path = os.path.abspath(sys.argv[0])
app_location=os.path.dirname(app_exe_path)

secret_location = os.path.join(app_location, ".secrets")


if not getattr(sys, 'frozen', False):
    app_exe_path=os.path.join(app_location, f"dist\\{app_name}\\{app_name}.exe")
    app_location=os.path.dirname(app_exe_path)

meipass_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")

icon_file = os.path.join(meipass_path, "icon.png")
style_file=os.path.join(meipass_path, "styles.qss")
refresh_icon_file=os.path.join(meipass_path, "refresh.png")

client_cert_file = os.path.join(secret_location, "client-cert.pem")
client_key_file = os.path.join(secret_location, "client-key.pem")
service_file = os.path.join(secret_location, "ls1-sample.json")


# update_file=os.path.join(app_location, "update.zip")
# updater_exe=os.path.join(app_location, "updater.exe")

