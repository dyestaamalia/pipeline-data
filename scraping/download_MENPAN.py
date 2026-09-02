import os
import glob
import shutil
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_FOLDER = r"F:\Magang\web_scraper"

def download_dataset(dataset, folder_name, file_prefix):
    # Download dataset MenPAN berdasarkan nama dataset.
    download_folder = os.path.join(BASE_FOLDER, folder_name)
    os.makedirs(download_folder, exist_ok=True)

    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    print(f"\n{file_prefix}")

    for tahun in range(2020, 2026):
        print(f"\nTahun {tahun}")

        download_url = (
            f"https://satudata.menpan.go.id/api/datasets/"
            f"{dataset}/download?format=xlsx&tahun={tahun}"
        )

        driver.get(download_url)
        print("Downloading...")
        time.sleep(5)

        files = glob.glob(os.path.join(download_folder, "*.xlsx"))

        if files:
            file_terbaru = max(files, key=os.path.getctime)

            tujuan = os.path.join(
                download_folder,
                f"{file_prefix}_{tahun}.xlsx"
            )

            if os.path.exists(tujuan):
                os.remove(tujuan)

            shutil.move(file_terbaru, tujuan)
            print(f"✔ {file_prefix}_{tahun}.xlsx")
        else:
            print(f"✘ File tahun {tahun} tidak ditemukan")

    driver.quit()

def gabung_dataset(folder_name, file_prefix):
    # Menggabungkan file dataset dari tahun 2020 sampai 2025.
    folder = os.path.join(BASE_FOLDER, folder_name)

    files = glob.glob(
        os.path.join(
            folder,
            f"{file_prefix}_*.xlsx"
        )
    )

    files = [
        file for file in files
        if f"{file_prefix}_Gabungan.xlsx" not in file
    ]

    if not files:
        print(f"✘ File {file_prefix} tidak ditemukan")
        return

    data = []

    for file in sorted(files):
        print(f"Menggabungkan {os.path.basename(file)}")

        df = pd.read_excel(file)

        data.append(df)

    hasil = pd.concat(
        data,
        ignore_index=True
    )

    output = os.path.join(
        folder,
        f"{file_prefix}_Gabungan.xlsx"
    )

    hasil.to_excel(
        output,
        index=False
    )

    print(f"✔ {file_prefix}_Gabungan.xlsx")

def main():
    download_dataset(
        dataset="spbe",
        folder_name="Menpan_SPBE",
        file_prefix="SPBE"
    )

    download_dataset(
        dataset="ipp",
        folder_name="Menpan_IPP",
        file_prefix="IPP"
    )

    download_dataset(
        dataset="sakip",
        folder_name="Menpan_sakip",
        file_prefix="SAKIP"
    )

    print("\nMenggabungkan dataset...")

    gabung_dataset(
        "Menpan_SPBE",
        "SPBE"
    )

    gabung_dataset(
        "Menpan_IPP",
        "IPP"
    )

    gabung_dataset(
        "Menpan_sakip",
        "SAKIP"
    )

    print("\nSELESAI")

if __name__ == "__main__":
    main()