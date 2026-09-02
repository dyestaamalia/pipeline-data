import os
import time
import glob
import shutil
import pandas as pd
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# PENYESUAIAN FOLDER
DOWNLOAD_FOLDER = r"F:\Magang\web_scraper\APBD-Indonesia"

# Pilih satu provinsi atau "SEMUA"
PROVINSI = "Provinsi Kalimantan Tengah"

# Tahun yang ingin diambil
TAHUN_MULAI = 2020
TAHUN_AKHIR = 2020

# Periode yang ingin diambil
PERIODE_MULAI = 11
PERIODE_AKHIR = 12


# FOLDER
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
for tahun in range(TAHUN_MULAI, TAHUN_AKHIR + 1):
    os.makedirs(
        os.path.join(DOWNLOAD_FOLDER, str(tahun)),
        exist_ok=True
    )


# CHROME
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": os.path.abspath(DOWNLOAD_FOLDER),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
wait = WebDriverWait(driver, 20)
url = "https://djpk.kemenkeu.go.id/portal/data/apbd"


# AMBIL DAFTAR PROVINSI
driver.get(url)
wait.until(
    EC.presence_of_element_located(
        (By.ID, "sel_provinsi")
    )
)
provinsi_options = Select(
    driver.find_element(By.ID, "sel_provinsi")
).options
provinsi_list = []
for option in provinsi_options:
    kode = option.get_attribute("value")
    nama = option.text.strip()
    if kode and nama:
        provinsi_list.append(
            (kode, nama)
        )


# PILIH PROVINSI
if PROVINSI.upper() == "SEMUA":
    provinsi_dipilih = provinsi_list
else:
    provinsi_dipilih = [
        (kode, nama)
        for kode, nama in provinsi_list
        if nama.lower() == PROVINSI.lower()
    ]
    if not provinsi_dipilih:
        print(
            f"Provinsi '{PROVINSI}' tidak ditemukan."
        )
        driver.quit()
        exit()


print("\nProvinsi yang diproses:")
for kode, nama in provinsi_dipilih:
    print(f"- {nama}")


# LOOP TAHUN
for tahun in range(
    TAHUN_MULAI,
    TAHUN_AKHIR + 1
):
    print(f"\n===== TAHUN {tahun} =====")

    # LOOP PROVINSI
    for kode_provinsi, nama_provinsi in provinsi_dipilih:
        print(f"\n--- {nama_provinsi} ---")

        # LOOP PERIODE
        for periode in range(PERIODE_MULAI, PERIODE_AKHIR + 1):
            print(f"Periode: {periode}")
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.ID, "sel_periode")))

            # Periode
            Select(driver.find_element(By.ID,"sel_periode")).select_by_value(str(periode))

            # Tahun
            Select(driver.find_element(By.ID, "sel_tahun")).select_by_value(str(tahun))

            time.sleep(2)

            # Provinsi
            Select(driver.find_element(By.ID,"sel_provinsi")).select_by_value(kode_provinsi)

            time.sleep(2)

            # AMBIL PEMDA
            pemda_options = Select(driver.find_element(By.ID,"sel_pemda")).options
            pemda_list = []
            for option in pemda_options:
                kode_pemda = option.get_attribute("value")
                nama_pemda = option.text.strip()
                if kode_pemda and nama_pemda:
                    pemda_list.append((kode_pemda,nama_pemda))

            print(f"Jumlah Pemda: {len(pemda_list)}")

            # LOOP PEMDA
            for kode_pemda, nama_pemda in pemda_list:
                print(f"Pemda: {nama_pemda}")
                try:

                    # Pilih Pemda
                    Select(driver.find_element(By.ID, "sel_pemda")).select_by_value(kode_pemda)

                    # Submit
                    driver.find_element(By.XPATH, "//button[@type='submit']").click()

                    # Tunggu tombol Excel
                    excel = wait.until(EC.element_to_be_clickable((By.ID,"link_csv")))

                    # Download
                    excel.click()
                    print("Downloading...")

                    # Tunggu download
                    time.sleep(6)

                    # CARI FILE HASIL DOWNLOAD
                    files = glob.glob(os.path.join(DOWNLOAD_FOLDER,"*.xls*"))
                    if not files:
                        print("✘ File tidak ditemukan")
                        continue

                    file_terbaru = max(files, key=os.path.getctime)
                    ext = os.path.splitext(file_terbaru)[1]


                    # BUAT FOLDER PROVINSI DAN PERIODE
                    folder_tujuan = os.path.join(
                        DOWNLOAD_FOLDER,
                        str(tahun),
                        nama_provinsi,
                        f"Periode_{periode}"
                    )
                    os.makedirs(folder_tujuan, exist_ok=True)


                    # NAMA FILE
                    nama_file = (
                        f"APBD_{tahun}_"
                        f"Periode_{periode}_"
                        f"{nama_pemda}"
                        f"{ext}"
                    )


                    tujuan = os.path.join(folder_tujuan, nama_file)

                    # Pindahkan file
                    if os.path.exists(tujuan):
                        os.remove(tujuan)

                    shutil.move(file_terbaru, tujuan)
                    print(f"✔ {nama_file}")


                except Exception as e:
                    print(f"✘ Gagal {nama_pemda}: {e}")


# SELESAI SCRAPING
driver.quit()
print("\n" + "=" * 50)
print("SCRAPING SELESAI")
print("=" * 50)


# FUNGSI BACA XML / XLS
def baca_xml(file):
    root = ET.parse(file).getroot()
    rows = []
    for row in root.iter():
        if not row.tag.endswith("Row"):
            continue
        data = []
        for cell in row:
            if cell.tag.endswith("Cell"):
                nilai = ""
                for child in cell:
                    if child.tag.endswith("Data"):
                        nilai = child.text or ""
                        break
                data.append(nilai)
        if data:
            rows.append(data)

    if not rows:
        raise ValueError("Data tidak ditemukan")

    jumlah_kolom = max(map(len, rows))

    rows = [
        r + [""] * (
            jumlah_kolom - len(r)
        )
        for r in rows
    ]

    return pd.DataFrame(
        rows[1:],
        columns=rows[0]
    )


# MULAI PENGGABUNGAN
semua_data = []

print("\n" + "=" * 50)
print("MULAI PENGGABUNGAN")
print("=" * 50)


for tahun in range(
    TAHUN_MULAI,
    TAHUN_AKHIR + 1
):
    folder_tahun = os.path.join(
        DOWNLOAD_FOLDER,
        str(tahun)
    )


    # Cari file XLS di dalam folder provinsi dan periode
    files = glob.glob(
        os.path.join(
            folder_tahun,
            "*",
            "Periode_*",
            "*.xls"
        )
    )


    print(f"\nTahun {tahun}: {len(files)} file")


    for file in sorted(files):
        nama_file = os.path.basename(file)

        # Ambil nama provinsi dari folder
        folder_periode = os.path.dirname(file)
        nama_provinsi = os.path.basename(
            os.path.dirname(folder_periode)
        )

        # Ambil periode dari folder
        nama_periode = os.path.basename(folder_periode)
        periode = nama_periode.replace(
            "Periode_",
            ""
        )

        print(
            f"Membaca: {nama_provinsi} - "
            f"{nama_periode} - "
            f"{nama_file}"
        )

        try:

            # Baca file
            df = baca_xml(file)

            # Bersihkan nama kolom
            df.columns = (df.columns.astype(str).str.strip())

            # Kolom APBD
            kolom = [
                "Akun",
                "Anggaran",
                "Realisasi",
                "Persentase"
            ]

            if not all(
                k in df.columns
                for k in kolom
            ):
                raise ValueError(
                    "Kolom APBD tidak lengkap"
                )

            df = df[kolom].copy()

            # Ambil nama Pemda dari nama file
            nama_pemda = os.path.splitext(nama_file)[0]

            nama_pemda = nama_pemda.replace(
                f"APBD_{tahun}_",
                ""
            )

            nama_pemda = nama_pemda.replace(
                f"Periode_{periode}_",
                ""
            )

            # Tambahkan informasi wilayah
            df.insert(0, "kab_kota", nama_pemda)
            df.insert(0, "periode", periode)
            df.insert(0, "tahun", tahun)
            df.insert(0, "provinsi", nama_provinsi)

            semua_data.append(df)

            print(f"  ✔ Berhasil: {len(df):,} baris")

        except Exception as e:
            print(f"  ✘ Gagal: {e}")


# SIMPAN HASIL GABUNGAN
if semua_data:
    hasil = pd.concat(semua_data, ignore_index=True)

    output = os.path.join(
        DOWNLOAD_FOLDER,
        "APBD_Indonesia_Gabungan.xlsx"
    )

    hasil.to_excel(output, index=False)

    print("\n" + "=" * 50)
    print("SEMUA PROSES SELESAI")
    print("=" * 50)

    print(f"Total file berhasil : {len(semua_data)}")
    print(f"Total baris         : {len(hasil):,}")
    print(f"File hasil          : {output}")

else:
    print("\n✘ Tidak ada data yang berhasil digabungkan.")