import os
from dotenv import load_dotenv
import paramiko
import stat  # <--- BU MUHIM!

# Rekursiv yuklab olish funksiyasi
def download_all(sftp, remote_path, local_path):
    os.makedirs(local_path, exist_ok=True)
    for entry in sftp.listdir_attr(remote_path):
        remote_item = f"{remote_path}/{entry.filename}"
        local_item = os.path.join(local_path, entry.filename)

        if stat.S_ISDIR(entry.st_mode):  # <-- TO‘G‘RILANDI
            # Agar bu papka bo‘lsa – rekursiv chaqiramiz
            download_all(sftp, remote_item, local_item)
        else:
            # Fayl bo‘lsa – yuklaymiz
            sftp.get(remote_item, local_item)
            print(f"✅ Yuklandi: {remote_item} ➜ {local_item}")

# .env fayldan o‘qish
load_dotenv(".env")
hostname = os.getenv("HOST")
port = int(os.getenv("PORT"))
username = os.getenv("SSH_USER")
password = os.getenv("PASSWORD")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=hostname, port=port, username=username, password=password)
    print("✅ SSH orqali ulanildi.")
    sftp = client.open_sftp()

    remote_dir = "/var/spool/asterisk/monitor"
    local_dir = "./downloads"

    download_all(sftp, remote_dir, local_dir)
    print("🎉 Hammasi yuklab olindi.")

finally:
    client.close()
    print("🔒 SSH ulanish yopildi.")
