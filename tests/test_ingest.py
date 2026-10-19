from datetime import datetime

from ingestion.ingest_weather import ensure_table, get_connection, to_rows, upsert


def test_to_rows_builds_rows_from_columns():
    payload = {
        "hourly": {
            "time": ["2026-10-17T00:00", "2026-10-17T01:00"],
            "temperature_2m": [8.1, 7.6],
            "precipitation": [0.0, 0.2],
        }
    }
    rows = to_rows("testcity", payload)
    assert rows == [
        ("testcity", datetime(2026, 10, 17, 0, 0), 8.1, 0.0),
        ("testcity", datetime(2026, 10, 17, 1, 0), 7.6, 0.2),
    ]


def test_upsert_is_idempotent():
    conn = get_connection()
    ensure_table(conn)
    rows = [
        ("pytest_city", datetime(2099, 1, 1, 0), 1.0, 0.0),
        ("pytest_city", datetime(2099, 1, 1, 1), 2.0, 0.5),
    ]
    try:
        upsert(conn, rows)
        upsert(conn, rows)  # zweiter Lauf mit denselben Daten
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM raw.weather_hourly WHERE city = 'pytest_city'")
            assert cur.fetchone()[0] == 2
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM raw.weather_hourly WHERE city = 'pytest_city'")
        conn.commit()
        conn.close()