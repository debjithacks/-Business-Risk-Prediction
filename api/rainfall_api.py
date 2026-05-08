import os

import requests
from dotenv import load_dotenv


load_dotenv()
_DEFAULT_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_rainfall(lat, lon, api_key: str | None = None):

    key = api_key or _DEFAULT_API_KEY
    if not key:
        raise RuntimeError(
            "Missing OpenWeatherMap API key. Set OPENWEATHER_API_KEY in your environment (or .env)."
        )

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}"

    response = requests.get(url, timeout=10)

    data = response.json()

    rainfall = data.get(
        "rain",
        {}
    ).get(
        "1h",
        0
    )

    return rainfall
