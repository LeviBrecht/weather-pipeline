select
    city,
    ts                  as hour_ts,
    temperature_2m      as temperature_c,
    precipitation       as precipitation_mm,
    ingested_at
from {{ source('raw', 'weather_hourly') }}