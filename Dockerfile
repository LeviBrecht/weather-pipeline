FROM apache/airflow:3.3.0

RUN pip install --no-cache-dir requests psycopg2-binary python-dotenv

# dbt in eigenem venv, damit es sich nicht mit Airflows Paketen beißt
RUN python -m venv /opt/airflow/dbt_venv \
    && /opt/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres