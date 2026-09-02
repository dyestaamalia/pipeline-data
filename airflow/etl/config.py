import os

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

GOOGLE_CREDENTIAL = os.getenv(
    "GOOGLE_CREDENTIAL",
    "/opt/airflow/config/credentials.json"
)

GOOGLE_FOLDER_ID = os.getenv("GOOGLE_FOLDER_ID")

# TARGET FILE

# Isi nama file jika hanya ingin memproses file tertentu.
#
# Contoh satu file:
# TARGET_FILES = [
#     "Dataset MENPAN.xlsx"
# ]
#
# Contoh beberapa file:
# TARGET_FILES = [
#     "Data APBD Jawa Barat 2020-2025.xlsx",
#     "Dataset MENPAN.xlsx"
# ]
#
# Kosong = proses SEMUA file di Google Drive.
# TARGET_FILES = []

TARGET_FILES = [
    "Data APBD Jawa Barat 2020-2025.xlsx"
]