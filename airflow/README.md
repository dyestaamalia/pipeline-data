# Data Integration Pipeline

Data Integration Pipeline merupakan project untuk melakukan proses ekstraksi, penyimpanan, cleaning, dan validation data menggunakan Apache Airflow, PostgreSQL, dbt, dan Docker.

## Requirements

Sebelum menjalankan project, pastikan sudah tersedia:

- Docker Desktop
- PostgreSQL
- pgAdmin
- Google Drive API Credentials

Pastikan Docker Desktop dalam keadaan aktif sebelum menjalankan project.

## Configuration

### Google Drive

Pipeline menggunakan Google Drive API untuk mengambil file sumber.

Gunakan Service Account credentials masing-masing dan simpan file sebagai:

```text
config/credentials.json
```

Pastikan Service Account telah diberikan akses ke folder Google Drive yang digunakan.

Gunakan `.env.example` sebagai template untuk membuat file `.env`, kemudian sesuaikan Google Drive Folder ID dan konfigurasi lainnya.

File yang ingin diproses dapat ditentukan melalui `TARGET_FILES` pada konfigurasi project.

```python
TARGET_FILES = [
    "Dataset MENPAN.xlsx"
]
```

Jika `TARGET_FILES` dikosongkan:

```python
TARGET_FILES = []
```

pipeline akan memproses seluruh file yang didukung pada folder Google Drive.

### PostgreSQL

Pastikan konfigurasi koneksi PostgreSQL sudah sesuai:

- Host
- Port
- Database
- Username
- Password

Konfigurasi koneksi dbt dapat diperiksa pada:

```text
dbt/profiles.yml
```

## Running the Project

Jalankan seluruh service menggunakan Docker Compose:

```bash
docker compose up -d
```

Periksa status container:

```bash
docker compose ps
```

Jika image perlu dibangun ulang:

```bash
docker compose up -d --build
```

## Running the Pipeline

Setelah container berjalan, buka Apache Airflow:

```text
http://localhost:8080
```

Cari DAG:

```text
data_integration_pipeline
```

Aktifkan DAG jika masih paused, kemudian klik **Trigger DAG**.

Pipeline menjalankan task berikut secara berurutan:

```text
extract_load >> dbt_clean >> dbt_validation
```

Status dan log setiap task dapat diperiksa melalui Airflow UI.

## Checking the Output

Hasil pipeline dapat diperiksa melalui PostgreSQL menggunakan pgAdmin:

```text
Schemas → public → Tables
```

Pipeline menghasilkan tabel raw, clean, dan validation.

Contoh:

```text
dataset_menpan_sakip
clean_dataset_menpan_sakip
validation_dataset_menpan_sakip
```

Untuk melihat hasil validation:

```sql
SELECT *
FROM public.validation_dataset_menpan_sakip;
```

## Stopping the Project

Untuk menghentikan seluruh service:

```bash
docker compose down
```

Untuk menjalankan kembali:

```bash
docker compose up -d
```

## Notes

File `.env` dan `credentials.json` tidak disertakan dalam repository.

Setiap pengguna harus menggunakan konfigurasi environment dan Google Drive API credentials masing-masing.

Jika terjadi error pada task pipeline, periksa **Logs** pada task terkait melalui Airflow UI.