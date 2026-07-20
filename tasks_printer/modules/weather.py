from ..jinja_env import env

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
        pass

    def render(self, p, context):
        weather = context.weather
        description = None
        if weather:
            description = WMO_CODE.get(weather.day_weather_code, f"Unknown weather code: {weather.day_weather_code}")

        rendered = env.get_template("weather.jinja").render(
            error=context.weather_error,
            temp_max=weather.day_temp_max if weather else None,
            temp_min=weather.day_temp_min if weather else None,
            description=description,
        ).rstrip("\n")
        p.text(rendered)
