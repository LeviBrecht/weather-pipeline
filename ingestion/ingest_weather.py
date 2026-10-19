import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CITIES_FILE = Path(__file__).resolve().parent / "cities.json"
API_URL = "https://api.open-meteo.com/v1/forecast"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ingest_weather")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def ensure_table(conn):
    """Legt die Zieltabelle an, falls sie noch nicht existiert."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS raw.weather_hourly (
                city            TEXT             NOT NULL,
                ts              TIMESTAMP        NOT NULL,
                temperature_2m  DOUBLE PRECISION,
                precipitation   DOUBLE PRECISION,
                ingested_at     TIMESTAMPTZ      NOT NULL DEFAULT now(),
                PRIMARY KEY (city, ts)
            )
            """
        )
    conn.commit()


def fetch_city(city):
    """Holt die Stundendaten einer Stadt von der API."""
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": "temperature_2m,precipitation",
        "past_days": 2,
        "timezone": "UTC",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()  # wirft einen Fehler bei HTTP 4xx/5xx
    return response.json()


def save_raw(city_name, payload):
    """Speichert die API-Antwort unverändert. Gleicher Tag = gleiche Datei (wird überschrieben)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = RAW_DIR / city_name / f"{today}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    return path


def to_rows(city_name, payload):
    """Setzt die drei Spalten-Listen der API zu Zeilen zusammen."""
    hourly = payload["hourly"]
    return [
        (city_name, datetime.fromisoformat(t), temp, precip)
        for t, temp, precip in zip(
            hourly["time"], hourly["temperature_2m"], hourly["precipitation"]
        )
    ]


def upsert(conn, rows):
    """Fügt Zeilen ein; existiert (city, ts) schon, werden die Werte aktualisiert."""
    sql = """
        INSERT INTO raw.weather_hourly (city, ts, temperature_2m, precipitation)
        VALUES %s
        ON CONFLICT (city, ts) DO UPDATE SET
            temperature_2m = EXCLUDED.temperature_2m,
            precipitation  = EXCLUDED.precipitation,
            ingested_at    = now()
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()


def main():
    cities = json.loads(CITIES_FILE.read_text(encoding="utf-8"))
    conn = get_connection()
    ensure_table(conn)

    failed = []
    for city in cities:
        name = city["name"]
        try:
            payload = fetch_city(city)
            path = save_raw(name, payload)
            rows = to_rows(name, payload)
            upsert(conn, rows)
            log.info("%s: %d Zeilen verarbeitet, Rohdatei %s", name, len(rows), path.name)
        except Exception:
            conn.rollback()
            log.exception("%s: Fehler beim Verarbeiten", name)
            failed.append(name)

    conn.close()
    if failed:
        log.error("Fehlgeschlagen: %s", ", ".join(failed))
        sys.exit(1)  # Exit-Code 1 -> Airflow erkennt später den Fehler


if __name__ == "__main__":
    main()