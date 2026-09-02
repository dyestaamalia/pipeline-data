# Cara Instalasi dan Menjalankan Program

## 1. Instalasi

Jalankan perintah berikut pada Command Prompt (CMD) atau Terminal untuk menginstal seluruh library yang dibutuhkan:

`pip install -r requirements.txt`

## 2. Menjalankan Program

### Download Dataset MenPAN

Sebelum menjalankan program, sesuaikan folder penyimpanan pada bagian **PENYESUAIAN FOLDER** di file `download_MENPAN.py`:

`BASE_FOLDER = r"F:\MAGANG\web_scraper"`

Ubah path tersebut sesuai dengan lokasi folder pada komputer yang digunakan.

Contoh:

`BASE_FOLDER = r"D:\Project\pipeline-data"`

Jalankan program menggunakan salah satu perintah berikut:

`py download_MENPAN.py` atau `python download_MENPAN.py`

Program akan mengunduh tiga dataset MenPAN:

* SPBE
* IPP
* SAKIP

Data yang diunduh adalah tahun 2020–2025.

#### Tahun

Jika ingin mengubah tahun yang diambil, ubah bagian berikut pada fungsi `download_dataset()`:

`for tahun in range(2020, 2026):`

Contoh untuk mengambil tahun 2022–2025:

`for tahun in range(2022, 2026):`

#### Dataset

Dataset yang digunakan dapat diubah pada bagian `main()`:

`dataset="spbe"`

`dataset="ipp"`

`dataset="sakip"`

Setelah proses download selesai, program akan otomatis menggabungkan data setiap dataset menjadi:

* `SPBE_Gabungan.xlsx`
* `IPP_Gabungan.xlsx`
* `SAKIP_Gabungan.xlsx`

---

### Download Dataset APBD

Sebelum menjalankan program, sesuaikan folder penyimpanan pada bagian **PENYESUAIAN FOLDER** di file `download_APBD.py`:

`DOWNLOAD_FOLDER = r"F:\MAGANG\web_scraper\APBD-Indonesia"`

Ubah path tersebut sesuai dengan lokasi folder pada komputer yang digunakan.

Contoh:

`DOWNLOAD_FOLDER = r"D:\Project\pipeline-data\APBD-Indonesia"`

#### Provinsi

Pada bagian:

`PROVINSI = "Provinsi Kalimantan Tengah"`

ubah nama provinsi sesuai data yang ingin diambil.

Contoh:

`PROVINSI = "Provinsi Jawa Barat"`

Jika ingin mengambil data dari seluruh provinsi, gunakan:

`PROVINSI = "SEMUA"`

#### Tahun

Untuk menentukan tahun yang ingin diambil, ubah:

`TAHUN_MULAI = 2020`

`TAHUN_AKHIR = 2020`

Contoh untuk mengambil data tahun 2020–2025:

`TAHUN_MULAI = 2020`

`TAHUN_AKHIR = 2025`

#### Periode

Untuk menentukan periode yang ingin diambil, ubah:

`PERIODE_MULAI = 11`

`PERIODE_AKHIR = 12`

Contoh untuk mengambil seluruh periode:

`PERIODE_MULAI = 1`

`PERIODE_AKHIR = 12`

Contoh untuk mengambil hanya periode Desember:

`PERIODE_MULAI = 12`

`PERIODE_AKHIR = 12`

Setelah pengaturan disesuaikan, jalankan program menggunakan salah satu perintah berikut:

`py download_APBD.py` atau `python download_APBD.py`

Tunggu hingga proses download selesai. Data APBD akan disimpan berdasarkan tahun, provinsi, dan periode yang dipilih.
