import re

from sqlalchemy import create_engine

from etl.utils import get_logger

logger = get_logger()


def normalize_table_name(table_name):

    table_name = str(table_name).strip().lower()

    # Ganti karakter selain huruf, angka, dan underscore
    table_name = re.sub(r"[^a-z0-9_]+", "_", table_name)

    # Hilangkan underscore berulang
    table_name = re.sub(r"_+", "_", table_name)

    # Hilangkan underscore di awal/akhir
    table_name = table_name.strip("_")

    # PostgreSQL maksimal 63 karakter
    return table_name[:63]


def load_postgres(
    df,
    database_url,
    table_name,
    mode="replace"
):
    try:

        logger.info("===== MEMULAI LOAD =====")

        # NORMALISASI NAMA TABEL
        normalized_name = normalize_table_name(table_name)

        logger.info(
            f"Nama tabel input      : {table_name}"
        )

        logger.info(
            f"Nama tabel PostgreSQL : {normalized_name}"
        )

        # CONNECT POSTGRESQL
        engine = create_engine(database_url)

        # LOAD DATA RAW
        df.to_sql(
            name=normalized_name,
            con=engine,
            if_exists=mode,
            index=False
        )

        logger.info(
            f"Data berhasil dimuat ke tabel "
            f"'{normalized_name}'"
        )

        logger.info(
            f"Jumlah data berhasil dimuat : {len(df)}"
        )

        logger.info("===== LOAD SELESAI =====")

        return normalized_name

    except Exception as e:

        logger.error(
            f"Gagal memuat data ke PostgreSQL: {e}"
        )

        raise