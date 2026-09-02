import io
import re
import importlib

import pandas as pd

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from etl import config
from etl.utils import get_logger


logger = get_logger()

# SANITIZE TABLE NAME
def sanitize_table_name(name):

    name = (
        str(name)
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    # Ganti karakter selain huruf, angka, underscore
    name = re.sub(
        r"[^a-z0-9_]",
        "",
        name
    )

    # Hilangkan underscore berulang
    name = re.sub(
        r"_+",
        "_",
        name
    )

    # Hilangkan underscore di awal / akhir
    name = name.strip("_")

    # PostgreSQL maksimal 63 karakter
    return name[:63]

# CLEAN STRUKTUR DATAFRAME
def clean_dataframe_structure(df):

    # HAPUS KOLOM UNNAMED

    df = df.loc[
        :,
        ~df.columns.astype(str).str.match(
            r"^Unnamed:",
            case=False
        )
    ]

    # HAPUS KOLOM YANG SELURUH NILAINYA KOSONG
    df = df.dropna(
        axis=1,
        how="all"
    )

    return df

# DOWNLOAD FILE KE MEMORY
def download_file(service, file_id):

    logger.info(
        "Mengunduh file..."
    )

    request = service.files().get_media(
        fileId=file_id
    )

    try:

        content = request.execute(
            num_retries=3
        )

        stream = io.BytesIO(
            content
        )

        stream.seek(0)

        logger.info(
            f"Download selesai : {len(content)} bytes"
        )

        return stream

    except Exception as e:

        logger.error(
            f"Gagal mengunduh file: {e}"
        )

        return None


# BACA CSV
def read_csv(stream):

    try:

        stream.seek(0)

        df = pd.read_csv(
            stream
        )

        return {
            "Sheet1": df
        }

    except Exception as e:

        logger.error(
            f"Gagal membaca CSV: {e}"
        )

        return None


# BACA EXCEL / HTML
def read_excel_or_html(
    stream,
    file_name
):
        # XLSX
    if file_name.lower().endswith(
        ".xlsx"
    ):

        try:

            stream.seek(0)

            excel = pd.read_excel(
                stream,
                sheet_name=None,
                engine="openpyxl"
            )

            logger.info(
                "File berhasil dibaca sebagai XLSX."
            )

            return excel

        except Exception as e:

            logger.error(
                f"Gagal membaca XLSX: {e}"
            )

            return None

    # XLS
    if file_name.lower().endswith(
        ".xls"
    ):

        try:

            stream.seek(0)

            excel = pd.read_excel(
                stream,
                sheet_name=None,
                engine="xlrd"
            )

            logger.info(
                "File berhasil dibaca sebagai XLS."
            )

            return excel

        except Exception as excel_error:

            logger.warning(
                "File .xls bukan XLS valid "
                "atau gagal dibaca xlrd."
            )

            logger.warning(
                f"Detail xlrd: {excel_error}"
            )

        try:

            logger.info(
                "Mencoba membaca file .xls sebagai HTML..."
            )

            stream.seek(0)

            tables = pd.read_html(
                stream
            )

            if not tables:

                raise ValueError(
                    "Tidak ditemukan HTML table."
                )

            excel = {}

            for index, df in enumerate(
                tables
            ):

                sheet_name = (
                    f"Sheet{index + 1}"
                )

                excel[
                    sheet_name
                ] = df

            logger.info(
                f"File .xls ternyata HTML "
                f"dengan {len(excel)} tabel."
            )

            return excel

        except Exception as html_error:

            logger.error(
                "Gagal membaca .xls sebagai HTML."
            )

            logger.error(
                f"Detail HTML: {html_error}"
            )

            return None

    return None

# EXTRACT GOOGLE DRIVE
def extract_from_drive(
    credential_path,
    folder_id
):

    # BACA CONFIG TERBARU
    importlib.reload(
        config
    )

    target_files = (
        config.TARGET_FILES
    )

    logger.info(
        "=" * 50
    )

    logger.info(
        "DATA INTEGRATION PIPELINE"
    )

    logger.info(
        "Menghubungkan ke Google Drive..."
    )

    logger.info(
        "=" * 50
    )

    logger.info(
        f"TARGET_FILES yang digunakan: "
        f"{target_files}"
    )

    # GOOGLE DRIVE AUTHENTICATION
    credentials = (
        Credentials
        .from_service_account_file(
            credential_path,
            scopes=[
                "https://www.googleapis.com/auth/drive.readonly"
            ]
        )
    )

    service = build(
        "drive",
        "v3",
        credentials=credentials
    )

    # AMBIL DAFTAR FILE
    logger.info(
        "Mengambil daftar file..."
    )

    results = (
        service
        .files()
        .list(
            q=(
                f"'{folder_id}' in parents "
                "and trashed=false"
            ),
            fields=(
                "files("
                "id,"
                "name,"
                "mimeType,"
                "shortcutDetails"
                ")"
            ),
            pageSize=1000
        )
        .execute()
    )

    files = results.get(
        "files",
        []
    )

    if not files:

        raise Exception(
            "Folder Google Drive kosong."
        )

    logger.info(
        f"Ditemukan {len(files)} file."
    )

    # MODE PEMROSESAN
    if target_files:

        logger.info(
            f"Mode TARGET FILES aktif : "
            f"{len(target_files)} file"
        )

        for target in target_files:

            logger.info(
                f"  - {target}"
            )

    else:

        logger.info(
            "Mode ALL FILES aktif : "
            "semua file yang didukung "
            "akan diproses."
        )

    datasets = []

    # PROSES SETIAP FILE
    for file in files:

        file_id = file[
            "id"
        ]

        file_name = file[
            "name"
        ]

        mime_type = file[
            "mimeType"
        ]

        # Nama file yang terlihat langsung
        # di folder Google Drive
        drive_file_name = (
            file_name
        )

        logger.info(
            "-" * 70
        )

        logger.info(
            f"Memproses : "
            f"{drive_file_name}"
        )

        # FILTER TARGET FILE
        if (
            target_files
            and drive_file_name
            not in target_files
        ):

            logger.info(
                f"{drive_file_name} "
                f"dilewati "
                f"(bukan TARGET_FILES)."
            )

            continue

        # HANDLE SHORTCUT
        if (
            mime_type
            ==
            "application/vnd.google-apps.shortcut"
        ):

            logger.info(
                "Shortcut terdeteksi."
            )

            shortcut_details = (
                file.get(
                    "shortcutDetails"
                )
            )

            if not shortcut_details:

                logger.warning(
                    "Shortcut tidak memiliki target."
                )

                continue

            target_id = (
                shortcut_details[
                    "targetId"
                ]
            )

            try:

                target = (
                    service
                    .files()
                    .get(
                        fileId=target_id,
                        fields=(
                            "id,"
                            "name,"
                            "mimeType"
                        )
                    )
                    .execute()
                )

            except Exception as e:

                logger.error(
                    f"Gagal membaca shortcut: {e}"
                )

                continue

            file_id = target[
                "id"
            ]

            file_name = target[
                "name"
            ]

            mime_type = target[
                "mimeType"
            ]

            logger.info(
                f"Target shortcut : "
                f"{file_name}"
            )

        # GOOGLE SHEETS
        if (
            mime_type
            ==
            "application/vnd.google-apps.spreadsheet"
        ):

            logger.info(
                "Google Sheets terdeteksi "
                "-> export XLSX"
            )

            try:

                request = (
                    service
                    .files()
                    .export_media(
                        fileId=file_id,
                        mimeType=(
                            "application/"
                            "vnd.openxmlformats-"
                            "officedocument."
                            "spreadsheetml.sheet"
                        )
                    )
                )

                content = (
                    request.execute(
                        num_retries=3
                    )
                )

                stream = io.BytesIO(
                    content
                )

                stream.seek(0)

                excel = pd.read_excel(
                    stream,
                    sheet_name=None,
                    engine="openpyxl"
                )

                logger.info(
                    "Google Sheets berhasil "
                    "diekspor dan dibaca."
                )

            except Exception as e:

                logger.error(
                    f"Gagal membaca "
                    f"Google Sheets: {e}"
                )

                continue

            file_type = (
                "google_sheets"
            )

        # FILE BIASA
        else:

            lower_name = (
                file_name.lower()
            )

            # TENTUKAN FORMAT FILE
            if lower_name.endswith(
                ".csv"
            ):

                file_type = (
                    "csv"
                )

            elif lower_name.endswith(
                ".xlsx"
            ):

                file_type = (
                    "excel"
                )

            elif lower_name.endswith(
                ".xls"
            ):

                file_type = (
                    "excel"
                )

            else:

                logger.warning(
                    f"{file_name} dilewati "
                    f"(format tidak didukung)."
                )

                continue

            logger.info(
                f"Format file : "
                f"{file_type}"
            )

            # DOWNLOAD FILE KE MEMORY

            stream = download_file(
                service,
                file_id
            )

            if stream is None:

                logger.warning(
                    f"{file_name} dilewati "
                    f"karena gagal diunduh."
                )

                continue

            # BACA CSV
            if file_type == "csv":

                logger.info(
                    "Membaca CSV..."
                )

                excel = read_csv(
                    stream
                )

                if excel is None:

                    logger.warning(
                        f"{file_name} dilewati "
                        f"karena gagal dibaca."
                    )

                    continue

            # BACA EXCEL / HTML
            else:

                logger.info(
                    "Membaca Excel..."
                )

                excel = (
                    read_excel_or_html(
                        stream,
                        file_name
                    )
                )

                if excel is None:

                    logger.warning(
                        f"{file_name} dilewati "
                        f"karena gagal dibaca."
                    )

                    continue

        # INFORMASI DATASET
        logger.info(
            f"Jumlah Sheet/Table : "
            f"{len(excel)}"
        )

        logger.info(
            f"Daftar Sheet/Table : "
            f"{list(excel.keys())}"
        )

        file_base = (
            file_name
            .rsplit(
                ".",
                1
            )[0]
        )

        # PROSES SETIAP SHEET / TABLE
        for sheet_name, df in excel.items():

            # BERSIHKAN STRUKTUR DATAFRAME
            original_columns = (
                len(df.columns)
            )

            df = (
                clean_dataframe_structure(
                    df
                )
            )

            cleaned_columns = (
                len(df.columns)
            )

            if (
                original_columns
                != cleaned_columns
            ):

                logger.info(
                    f"Kolom kosong / Unnamed "
                    f"dihapus : "
                    f"{original_columns} "
                    f"-> "
                    f"{cleaned_columns}"
                )

            # BUAT NAMA TABEL
            table_name = (
                sanitize_table_name(
                    f"{file_base}_"
                    f"{sheet_name}"
                )
            )

            logger.info(
                "-" * 50
            )

            logger.info(
                f"Sheet   : "
                f"{sheet_name}"
            )

            logger.info(
                f"Tabel   : "
                f"{table_name}"
            )

            logger.info(
                f"Rows    : "
                f"{len(df)}"
            )

            logger.info(
                f"Columns : "
                f"{len(df.columns)}"
            )

            # SKIP DATAFRAME KOSONG
            if df.empty:

                logger.warning(
                    f"{table_name} kosong. "
                    f"Dilewati."
                )

                continue

            # TAMBAHKAN DATASET KE PIPELINE
            datasets.append(
                {
                    "table_name": (
                        table_name
                    ),
                    "df": df
                }
            )

            logger.info(
                f"{table_name} berhasil "
                f"ditambahkan ke pipeline."
            )

    logger.info(
        "=" * 70
    )

    logger.info(
        f"Total Dataset : "
        f"{len(datasets)}"
    )

    logger.info(
        "Extract Google Drive selesai."
    )

    logger.info(
        "=" * 70
    )

    return datasets