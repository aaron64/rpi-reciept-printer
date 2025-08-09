import requests
import json
from datetime import datetime, timezone

API_GET_WEATHER = "https://api.open-meteo.com/v1/forecast" 

WMO_CODE = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

class ModuleWeather:
    def __init__(self, config):
        self.error_message = None
        
        try:
            # Check for required config keys
            if 'latitude' not in config or 'longitude' not in config:
                self.error_message = "Weather config missing latitude/longitude"
                return
            
            params = {
                "latitude": config['latitude'],
                "longitude": config['longitude'],
                "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code"],
                "timezone": config.get('timezone', 'America/Los_Angeles'),
                "forecast_days": 1,
                "temperature_unit": "fahrenheit"
            }
            
            response = requests.request("GET", API_GET_WEATHER, params=params)
            
            if response.status_code != 200:
                self.error_message = f"Weather API error: {response.status_code}"
                return
                
            day_json = response.json()['daily']

            self.day_temp_min = day_json['temperature_2m_min'][0]
            self.day_temp_max = day_json['temperature_2m_max'][0]
            self.day_weather_code = day_json['weather_code'][0]
            
        except KeyError as e:
            self.error_message = f"Weather config missing key: {e}"
        except requests.exceptions.RequestException as e:
            self.error_message = f"Weather API request failed: {e}"
        except Exception as e:
            self.error_message = f"Weather data error: {e}"

    def reciept_print(self, p):
        if self.error_message:
            p.text(f"Weather data unavailable: {self.error_message}")
            return
            
        weather_string = f"{self.day_temp_max}°F/{self.day_temp_min}°F "
        if self.day_weather_code in WMO_CODE:
            weather_string += f"{WMO_CODE[self.day_weather_code]}"
        else:
            weather_string += f"Unknown weather code: {self.day_weather_code}"
        p.text(weather_string)
