import sys
import subprocess
import json
from datetime import datetime

sys.path.append("/opt/airflow")

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from etl.pipeline import run_pipeline

# DBT CLEAN
def run_dbt_clean(**context):

    loaded_tables = context["ti"].xcom_pull(
        task_ids="extract_load"
    )

    if not loaded_tables:
        print("Tidak ada tabel yang berhasil di-load.")
        return

    for table in loaded_tables:

        print("=" * 70)
        print(f"DBT CLEAN : {table}")
        print("=" * 70)

        command = [
            "dbt",
            "run",
            "--project-dir",
            "/opt/airflow/dbt",
            "--profiles-dir",
            "/opt/airflow/dbt",
            "--select",
            "clean",
            "--vars",
            json.dumps({
                "source_table": table
            })
        ]

        subprocess.run(
            command,
            check=True
        )

# DBT VALIDATION
def run_dbt_validation(**context):

    loaded_tables = context["ti"].xcom_pull(
        task_ids="extract_load"
    )

    if not loaded_tables:
        print("Tidak ada tabel yang berhasil di-load.")
        return

    for table in loaded_tables:

        print("=" * 70)
        print(f"DBT VALIDATION : {table}")
        print("=" * 70)

        command = [
            "dbt",
            "run",
            "--project-dir",
            "/opt/airflow/dbt",
            "--profiles-dir",
            "/opt/airflow/dbt",
            "--select",
            "validation",
            "--vars",
            json.dumps({
                "source_table": table
            })
        ]

        subprocess.run(
            command,
            check=True
        )

# DAG
with DAG(
    dag_id="data_integration_pipeline",
    description="ETL Google Drive to PostgreSQL with dbt",
    start_date=datetime(2026, 7, 19),
    schedule=None,
    catchup=False,
    tags=["ETL", "Google Drive", "dbt"],
) as dag:

    # EXTRACT + LOAD
    extract_load = PythonOperator(
        task_id="extract_load",
        python_callable=run_pipeline,
    )

    # DBT CLEAN
    dbt_clean = PythonOperator(
        task_id="dbt_clean",
        python_callable=run_dbt_clean,
    )

    # DBT VALIDATION
    dbt_validation = PythonOperator(
        task_id="dbt_validation",
        python_callable=run_dbt_validation,
    )

    extract_load >> dbt_clean >> dbt_validation