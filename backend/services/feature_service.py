# backend/services/feature_service.py
from datetime import datetime
from .model_service import date_to_numeric

# ---------- Agro zone mapping ----------
MARKET_TO_AGROZONE = {
    "Purba Medinipur": "Coastal Saline",

    "Darjeeling": "Hill Zone",
    "Kalimpong": "Hill Zone",

    "Dakshin Dinajpur": "New Alluvial",
    "Howrah": "New Alluvial",
    "Kolkata": "New Alluvial",
    "Malda": "New Alluvial",
    "Uttar Dinajpur": "New Alluvial",

    "Hooghly": "Old Alluvial",
    "Murshidabad": "Old Alluvial",
    "Nadia": "Old Alluvial",
    "North 24 Parganas": "Old Alluvial",
    "South 24 Parganas": "Old Alluvial",

    "Bankura": "Red Laterite",
    "Jhargram": "Red Laterite",
    "Paschim Medinipur": "Red Laterite",
    "Purulia": "Red Laterite",

    "Alipurduar": "Terai",
    "Cooch Behar": "Terai",
    "Jalpaiguri": "Terai",

    "Birbhum": "Western Plateau Transition Zone",
    "Paschim Bardhaman": "Western Plateau Transition Zone",
    "Purba Bardhaman": "Western Plateau Transition Zone",
}

# ---------- Nearby markets (for comparison) ----------
NEARBY_MARKETS = {
    "Kolkata": ["Howrah", "North 24 Parganas", "Hooghly"],
    "Howrah": ["Kolkata", "Hooghly", "North 24 Parganas"],
    "Hooghly": ["Kolkata", "Howrah", "Nadia"],
    "Nadia": ["Hooghly", "North 24 Parganas", "Murshidabad"],
    "North 24 Parganas": ["Kolkata", "Howrah", "Nadia"],
    "South 24 Parganas": ["Kolkata", "North 24 Parganas", "Howrah"],
    "Purba Medinipur": ["Paschim Medinipur", "Howrah", "South 24 Parganas"],
    "Paschim Medinipur": ["Purba Medinipur", "Jhargram", "Bankura"],
    "Jhargram": ["Paschim Medinipur", "Bankura", "Purulia"],
    "Bankura": ["Paschim Medinipur", "Purulia", "Birbhum"],
    "Birbhum": ["Bankura", "Purba Bardhaman", "Murshidabad"],
    "Purba Bardhaman": ["Paschim Bardhaman", "Birbhum", "Nadia"],
    "Paschim Bardhaman": ["Purba Bardhaman", "Bankura", "Birbhum"],
    "Murshidabad": ["Nadia", "Malda", "Birbhum"],
    "Malda": ["Murshidabad", "Dakshin Dinajpur", "Uttar Dinajpur"],
    "Dakshin Dinajpur": ["Malda", "Uttar Dinajpur"],
    "Uttar Dinajpur": ["Dakshin Dinajpur", "Malda"],
    "Alipurduar": ["Cooch Behar", "Jalpaiguri"],
    "Cooch Behar": ["Alipurduar", "Jalpaiguri"],
    "Jalpaiguri": ["Darjeeling", "Cooch Behar", "Alipurduar"],
    "Darjeeling": ["Jalpaiguri", "Kalimpong"],
    "Kalimpong": ["Darjeeling", "Jalpaiguri"],
    "Purulia": ["Bankura", "Jhargram"],
}

def get_nearby_markets(market: str, k: int = 3):
    """Return up to k nearby markets (simple mapping)."""
    if market in NEARBY_MARKETS:
        return NEARBY_MARKETS[market][:k]
    # fallback: any other markets in mapping
    all_markets = [m for m in MARKET_TO_AGROZONE.keys() if m != market]
    return all_markets[:k]

# ---------- Utility functions ----------

def detect_season(dt: datetime) -> str:
    m = dt.month
    if 6 <= m <= 10:
        return "Kharif"
    elif 11 <= m or m <= 3:
        return "Rabi"
    else:
        return "Pre-Kharif"

def determine_agrozone(market: str) -> str:
    return MARKET_TO_AGROZONE.get(market, "New Alluvial")

def approx_soil_moisture(humidity: float, rainfall_mm: float) -> float:
    base = 20 + 0.3 * humidity + 0.5 * rainfall_mm
    return max(10.0, min(80.0, base))

def approx_economic_indices(crop: str, dt: datetime):
    month_factor = dt.month / 12.0
    demand_index = 0.4 + 0.4 * month_factor
    supply_quintals = 800 + 400 * (1 - month_factor)
    fuel_price_index = 1.0 + 0.1 * month_factor
    inflation_rate = 5.5 + 0.5 * month_factor
    commodity_trend = 0.5 + 0.3 * month_factor
    return {
        "DemandIndex": round(demand_index, 3),
        "Supply(quintals)": round(supply_quintals, 2),
        "FuelPriceIndex": round(fuel_price_index, 3),
        "InflationRate(%)": round(inflation_rate, 3),
        "CommodityTrendIndex": round(commodity_trend, 3),
    }

def build_feature_vector(crop: str, market: str, date_str: str,
                         lat: float, lon: float, weather_current: dict):
    dt = datetime.fromisoformat(date_str)
    season = detect_season(dt)
    agrozone = determine_agrozone(market)

    rain = float(weather_current["rainfall_mm"] or 0.0)
    temp = float(weather_current["temp_c"])
    humidity = float(weather_current["humidity"])
    soil_moisture = approx_soil_moisture(humidity, rain)
    econ = approx_economic_indices(crop, dt)

    feat = {
        "Crop": crop,
        "Market": market,
        "AgroZone": agrozone,
        "Season": season,
        "Rainfall(mm)": rain,
        "AvgTemperature(°C)": temp,
        "Humidity(%)": humidity,
        "SoilMoisture(%)": soil_moisture,
        "DemandIndex": econ["DemandIndex"],
        "Supply(quintals)": econ["Supply(quintals)"],
        "FuelPriceIndex": econ["FuelPriceIndex"],
        "InflationRate(%)": econ["InflationRate(%)"],
        "CommodityTrendIndex": econ["CommodityTrendIndex"],
        "DateNumeric": date_to_numeric(dt),
    }
    return feat
