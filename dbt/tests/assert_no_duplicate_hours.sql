select
    city,
    hour_ts,
    count(*) as n
from {{ ref('stg_weather_hourly') }}
group by city, hour_ts
having count(*) > 1