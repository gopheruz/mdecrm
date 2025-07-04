import os
import psycopg2
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# Sozlamalarni o‘qib olish
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = '84.54.115.43'

DB_PORT = os.getenv('DB_PORT')

# Ulanish
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("Muvaffaqiyatli ulandi!")
except Exception as e:
    print("Xatolik:", e)
