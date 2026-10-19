small data engineering project
# Weather Pipeline

Kleines Data-Engineering-Lernprojekt: Eine End-to-End-Pipeline, die stündliche Wetterdaten für fünf Städte von der kostenlosen Open-Meteo-API holt, speichert, transformiert und visualisiert.

## Ziel

- Den typischen Data-Engineering-Ablauf praktisch lernen: Ingestion → Speicherung → Transformation → Orchestrierung → Reporting
- Best Practices üben: Idempotenz, Raw-Schicht, Konfiguration statt Hardcoding, Tests, Versionskontrolle

## Architektur

```
Open-Meteo API → Python-Skript → data/raw/*.json (unverändertes Archiv)
                      ↓
              Postgres: raw.weather_hourly (idempotenter Upsert)
                      ↓
              dbt: staging → marts
                      ↓
              Power BI Desktop
        Airflow (Docker Compose) steuert den stündlichen Lauf
```

## Tech-Stack

- **Datenquelle:** Open-Meteo Forecast API (kostenlos, ohne API-Key)
- **Ingestion:** Python (requests, psycopg2)
- **Speicherung:** PostgreSQL 16 in Docker
- **Transformation:** dbt (dbt-postgres)
- **Orchestrierung:** Apache Airflow (lokal per Docker Compose)
- **Reporting:** Power BI Desktop
- **Tests:** pytest, später dbt-Tests
