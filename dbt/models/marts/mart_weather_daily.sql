select
    city,
    cast(hour_ts as date)                         as date_utc,
    min(temperature_c)                            as temp_min_c,
    max(temperature_c)                            as temp_max_c,
    round(avg(temperature_c)::numeric, 1)         as temp_avg_c,
    round(sum(precipitation_mm)::numeric, 1)      as precipitation_sum_mm,
    count(*)                                      as hours_count
from {{ ref('stg_weather_hourly') }}
group by city, cast(hour_ts as date)