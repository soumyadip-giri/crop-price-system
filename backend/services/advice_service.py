# backend/services/advice_service.py
from datetime import datetime, timedelta

# Approximate global model metrics from training (tune with real values if you have them)
GLOBAL_MAE = 6.0
GLOBAL_RMSE = 8.0


def compute_confidence_range(price: float):
    """
    Simple symmetric band around prediction using RMSE.
    """
    lower = max(0.0, price - GLOBAL_RMSE)
    upper = price + GLOBAL_RMSE
    return lower, upper


def generate_advice(predicted_price: float, future_prices: list):
    """
    Core economic advice based on price trend.
    """
    if not future_prices:
        return ("Based on current conditions, this is the estimated price. "
                "Consider checking again closer to your selling date.")

    future_avg = sum(future_prices) / len(future_prices)
    diff = future_avg - predicted_price

    if diff > 5:
        return ("Prices are likely to increase in the coming days. "
                "If possible, you may wait before selling.")
    elif diff < -5:
        return ("Prices may fall in the coming days. "
                "It could be better to sell earlier.")
    else:
        return ("Prices are relatively stable. "
                "You can sell as per your convenience and storage capacity.")


def get_trend_direction(today_price: float, future_prices: list):
    if not future_prices:
        return "flat"
    avg_future = sum(future_prices) / len(future_prices)
    diff = avg_future - today_price
    if diff > 3:
        return "up"
    if diff < -3:
        return "down"
    return "flat"


def get_best_day_info(base_date: datetime, future_prices: list):
    """
    Given the base selling date and list of future prices (next 3 days),
    return the best day suggestion as a small dict.
    """
    if not future_prices:
        return None
    best_idx = max(range(len(future_prices)), key=lambda i: future_prices[i])
    best_price = future_prices[best_idx]
    best_date = base_date + timedelta(days=best_idx + 1)
    label = best_date.strftime("%a %d-%b")
    return {
        "date": best_date.date().isoformat(),
        "label": label,
        "price": float(best_price),
    }


# ---------- Agro suitability & risks ----------

def crop_suitability_level(crop: str, temp_c: float, rainfall_mm: float, soil_moisture: float):
    """
    Very simple rule-based classification into ideal / moderate / stressful.
    """
    if 20 <= temp_c <= 32 and 20 <= soil_moisture <= 60 and rainfall_mm <= 25:
        level = "ideal"
        msg = "Weather and soil moisture look ideal for healthy crop growth."
    elif 15 <= temp_c <= 35 and 15 <= soil_moisture <= 70 and rainfall_mm <= 50:
        level = "moderate"
        msg = "Conditions are acceptable but monitor field closely for stress."
    else:
        level = "stressful"
        msg = "Conditions may stress the crop. Plan irrigation/drainage and monitor carefully."
    return level, msg


def disease_risk_hint(crop: str, temp_c: float, humidity: float):
    if humidity > 80 and 18 <= temp_c <= 32:
        return ("High humidity and moderate temperature increase risk of fungal diseases. "
                "Ensure good drainage and avoid waterlogging.")
    if humidity < 40 and temp_c > 32:
        return ("Low humidity and high temperature may cause moisture stress. "
                "Irrigate timely and use mulching if possible.")
    return ("No major weather-based disease risk detected, but continue routine crop protection practices.")


def extreme_events_hint(forecast_weather: list):
    heavy_days = [d for d in forecast_weather if d.get("rainfall_mm", 0) > 40]
    if heavy_days:
        dates = ", ".join(d["date"] for d in heavy_days)
        return f"Heavy rainfall expected on {dates}. Plan harvesting, storage and field drainage accordingly."
    return "No extreme rainfall events detected in the next few days."


def generate_agro_insights(crop: str, current_weather: dict, soil_moisture: float, forecast_weather: list):
    temp_c = float(current_weather.get("temp_c", 0))
    rainfall_mm = float(current_weather.get("rainfall_mm", 0))
    humidity = float(current_weather.get("humidity", 0))

    level, suit_msg = crop_suitability_level(crop, temp_c, rainfall_mm, soil_moisture)
    disease_msg = disease_risk_hint(crop, temp_c, humidity)
    extreme_msg = extreme_events_hint(forecast_weather)

    return {
        "suitabilityLevel": level,
        "suitabilityText": suit_msg,
        "diseaseRisk": disease_msg,
        "extremeWarning": extreme_msg,
    }


# ---------- Simple "feature importance" story ----------

def explain_features(feat: dict, weather_current: dict):
    """
    Not true SHAP – just a human-readable summary of which factors look important
    for this particular prediction.
    """
    messages = []

    # Seasonality
    messages.append("Season and date (capturing typical seasonal price patterns).")

    # Demand / supply
    if feat.get("DemandIndex", 0) > 0.7:
        messages.append("High demand index pushing the price upward.")
    elif feat.get("DemandIndex", 0) < 0.5:
        messages.append("Lower demand index keeping prices under pressure.")

    if feat.get("Supply(quintals)", 0) > 900:
        messages.append("High supply in markets, putting downward pressure on price.")
    else:
        messages.append("Relatively tight supply, supporting higher prices.")

    # Weather
    rain = float(weather_current.get("rainfall_mm", 0))
    temp = float(weather_current.get("temp_c", 0))
    if rain > 20:
        messages.append("Recent rainfall influencing harvesting and transport, affecting prices.")
    if temp > 32:
        messages.append("Higher temperature can stress crops and impact yield expectations.")

    # Keep top 3–4 unique messages
    seen = set()
    out = []
    for m in messages:
        if m not in seen:
            seen.add(m)
            out.append(m)
        if len(out) >= 4:
            break
    return out
