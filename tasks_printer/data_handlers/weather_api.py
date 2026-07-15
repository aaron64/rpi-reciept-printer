import requests
from dataclasses import dataclass

API_GET_WEATHER = "https://api.open-meteo.com/v1/forecast"


@dataclass
class WeatherData:
    day_temp_min: float
    day_temp_max: float
    day_weather_code: int


def fetch_weather(latitude, longitude, timezone='America/Los_Angeles'):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code"],
        "timezone": timezone,
        "forecast_days": 1,
        "temperature_unit": "fahrenheit"
    }

    response = requests.get(API_GET_WEATHER, params=params)
    response.raise_for_status()

    day_json = response.json()['daily']
    return WeatherData(
        day_temp_min=day_json['temperature_2m_min'][0],
        day_temp_max=day_json['temperature_2m_max'][0],
        day_weather_code=day_json['weather_code'][0],
    )
