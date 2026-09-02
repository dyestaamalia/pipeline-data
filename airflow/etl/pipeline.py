from etl.google_drive import extract_from_drive
from etl.load import load_postgres
from etl.config import (
    DATABASE_URL,
    GOOGLE_CREDENTIAL,
    GOOGLE_FOLDER_ID,
)


def run_pipeline():

    print("=" * 50)
    print("DATA INTEGRATION PIPELINE")
    print("=" * 50)

    # EXTRACT
    datasets = extract_from_drive(
        credential_path=GOOGLE_CREDENTIAL,
        folder_id=GOOGLE_FOLDER_ID,
    )

    print(f"Jumlah dataset ditemukan : {len(datasets)}")

    # Menyimpan semua tabel yang berhasil di-load
    loaded_tables = []

    # LOAD
    for dataset in datasets:

        table_name = dataset["table_name"]
        df = dataset["df"]

        print("-" * 70)
        print(f"Memproses : {table_name}")

        load_postgres(
            df=df,
            database_url=DATABASE_URL,
            table_name=table_name,
            mode="replace",
        )

        # Simpan nama tabel yang berhasil di-load
        loaded_tables.append(table_name)

        print(
            f"{table_name} selesai "
            f"({len(df)} rows)"
        )

    # SELESAI
    print("=" * 50)
    print("EXTRACT & LOAD SELESAI")
    print("=" * 50)

    print(f"Total tabel berhasil di-load : {len(loaded_tables)}")

    for table in loaded_tables:
        print(f"  - {table}")

    print("=" * 50)

    return loaded_tables