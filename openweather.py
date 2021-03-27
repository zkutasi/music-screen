import logging
import urllib

import httpclient
import settings



_LOGGER = logging.getLogger(__name__)
OPENWEATHER_API_URL_ROOT = 'http://api.openweathermap.org/data/2.5/weather?'
OPENWEATHER_API_URL_QUERY = '{root}q={city}&appid={apikey}&units={units}'.format(
    root=OPENWEATHER_API_URL_ROOT,
    city=settings.OpenWeatherConfig.OPENWEATHER_CITY,
    apikey=settings.OpenWeatherConfig.OPENWEATHER_APIKEY,
    units=settings.OpenWeatherConfig.OPENWEATHER_UNITS
)



def get_weather_for_city():
    return httpclient.get_json_from_url(OPENWEATHER_API_URL_QUERY)