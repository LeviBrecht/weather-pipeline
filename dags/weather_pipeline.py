from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

DBT = "/opt/airflow/dbt_venv/bin/dbt"
DBT_DIR = "/opt/airflow/dbt"

with DAG(
    dag_id="weather_pipeline",
    description="Open-Meteo: Ingestion -> dbt run -> dbt test",
    start_date=datetime(2026, 10, 1),
    schedule="@hourly",
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["weather"],
) as dag:
    ingest = BashOperator(
        task_id="ingest",
        bash_command="python /opt/airflow/ingestion/ingest_weather.py",
    )
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && {DBT} run",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && {DBT} test",
    )

    ingest >> dbt_run >> dbt_test