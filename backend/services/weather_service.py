# backend/services/weather_service.py
import requests
from datetime import datetime, timezone
from .. import config

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"  # 5 day / 3-hour


class WeatherServiceError(RuntimeError):
    pass


def _check_api_key():
    """
    Ensure a real OpenWeather API key is configured.
    If not, raise an error so the frontend can show a proper message.
    """
    key = config.OPENWEATHER_API_KEY
    if not key or not key.strip() or key == "YOUR_OPENWEATHER_API_KEY":
        raise WeatherServiceError(
            "OpenWeather API key is not configured. "
            "Set environment variable OPENWEATHER_API_KEY (or .env) with your real key."
        )


def _handle_response(resp):
    if resp.status_code != 200:
        try:
            data = resp.json()
            msg = data.get("message", "")
        except Exception:
            msg = resp.text
        raise WeatherServiceError(f"OpenWeather error {resp.status_code}: {msg}")


def get_weather_and_forecast(lat: float, lon: float):
    """
    Returns LIVE OpenWeather data:
        current: { temp_c, humidity, rainfall_mm, description }
        forecast: list[{ date, temp_c, rainfall_mm }]  (next ~5 days)

    If the key is missing or the API call fails, this raises WeatherServiceError.
    The /api/predict route will return a 502 with the error details.
    """
    _check_api_key()

    # ----- current weather -----
    params_cur = {
        "lat": lat,
        "lon": lon,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "metric",
    }
    resp_cur = requests.get(WEATHER_URL, params=params_cur, timeout=10)
    _handle_response(resp_cur)
    cur = resp_cur.json()

    rain_cur = 0.0
    if "rain" in cur:
        if isinstance(cur["rain"], dict):
            rain_cur = float(cur["rain"].get("1h") or cur["rain"].get("3h") or 0.0)
        else:
            rain_cur = float(cur["rain"])

    current_out = {
        "temp_c": float(cur["main"]["temp"]),
        "humidity": float(cur["main"]["humidity"]),
        "rainfall_mm": rain_cur,
        "description": cur.get("weather", [{}])[0].get("description", ""),
    }

    # ----- forecast (5-day / 3-hour, aggregated to daily) -----
    params_fc = {
        "lat": lat,
        "lon": lon,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "metric",
    }
    resp_fc = requests.get(FORECAST_URL, params=params_fc, timeout=10)
    _handle_response(resp_fc)
    fc = resp_fc.json()

    daily = {}
    for item in fc.get("list", []):
        dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        date_str = dt.date().isoformat()
        temp = float(item["main"]["temp"])

        rain_val = 0.0
        if "rain" in item:
            if isinstance(item["rain"], dict):
                rain_val = float(item["rain"].get("3h", 0.0))
            else:
                rain_val = float(item["rain"])

        if date_str not in daily:
            daily[date_str] = {"temp_sum": 0.0, "count": 0, "rain_sum": 0.0}
        daily[date_str]["temp_sum"] += temp
        daily[date_str]["rain_sum"] += rain_val
        daily[date_str]["count"] += 1

    forecast = []
    for date_str in sorted(daily.keys())[:5]:
        entry = daily[date_str]
        forecast.append(
            {
                "date": date_str,
                "temp_c": entry["temp_sum"] / entry["count"],
                "rainfall_mm": entry["rain_sum"],
            }
        )

    return current_out, forecast
