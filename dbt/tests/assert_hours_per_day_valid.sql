select *
from {{ ref('mart_weather_daily') }}
where hours_count > 24