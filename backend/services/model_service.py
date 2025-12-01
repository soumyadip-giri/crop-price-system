# backend/services/model_service.py

import os
from datetime import datetime

import joblib
import pandas as pd
import requests

from .. import config

# ----------------- model file & download -----------------

_model = None

# You can either:
# 1) set MODEL_URL in environment (for cloud/Render), OR
# 2) copy the trained .pkl file into ml/ and set MODEL_PATH, OR
# 3) for local testing only, rely on the fallback dummy model.
DEFAULT_MODEL_URL = (
    "https://drive.google.com/uc?export=download&id=1ZUNbmS6h6WFd6ja2Z1OoGKJi5FxToot9"
)  # optional fallback URL

# final URL we will try to use for download if local file is missing
MODEL_URL = os.getenv("MODEL_URL") or DEFAULT_MODEL_URL

FEATURE_COLUMNS = [
    "Crop",
    "Market",
    "AgroZone",
    "Season",
    "Rainfall(mm)",
    "AvgTemperature(°C)",
    "Humidity(%)",
    "SoilMoisture(%)",
    "DemandIndex",
    "Supply(quintals)",
    "FuelPriceIndex",
    "InflationRate(%)",
    "CommodityTrendIndex",
    "DateNumeric",
]


def _download_model_if_needed():
    """
    If the model file doesn't exist, try to download it from MODEL_URL
    and save it to config.MODEL_PATH.

    For local dev, if this fails we will fall back to a dummy model (see _load_model()).
    """
    # If file already exists, nothing to do
    if os.path.exists(config.MODEL_PATH):
        return

    if not MODEL_URL or "YOUR_FILE_ID" in MODEL_URL:
        # No usable URL configured – just let caller decide what to do.
        raise RuntimeError(
            "MODEL_URL is not set or invalid, and model file is missing at "
            f"{config.MODEL_PATH}. For local dev either copy the model file "
            "to that path or ignore this if you are using the dummy model fallback."
        )

    os.makedirs(os.path.dirname(config.MODEL_PATH), exist_ok=True)

    resp = requests.get(MODEL_URL, stream=True, timeout=60)
    resp.raise_for_status()

    with open(config.MODEL_PATH, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def _create_dummy_model(reason: str):
    """
    Very simple fallback model for local/offline testing.
    It ignores crop/market details and returns a reasonable price based on
    a few economic features if available.
    """

    class _DummyModel:
        def __init__(self, reason_text: str):
            self.reason = reason_text

        def predict(self, X: pd.DataFrame):
            # Try to use some features to produce a somewhat varying price
            try:
                base = 25.0
                if "CommodityTrendIndex" in X.columns:
                    base += 5.0 * float(X["CommodityTrendIndex"].iloc[0] - 0.5)
                if "DemandIndex" in X.columns:
                    base += 4.0 * float(X["DemandIndex"].iloc[0] - 0.5)
                if "Rainfall(mm)" in X.columns:
                    # Slight discount if very high rainfall
                    rain = float(X["Rainfall(mm)"].iloc[0])
                    base -= 0.05 * max(0.0, rain - 20)
                # Keep in a reasonable range
                price = max(5.0, min(80.0, base))
            except Exception:
                price = 25.0
            # Return a 1-element list, like a real sklearn model
            return [price]

    print(
        "WARNING: Using DummyModel fallback for predictions. Reason:",
        reason,
    )
    return _DummyModel(reason)


def _load_model():
    """
    Load the ML model, downloading it first if necessary.

    For local testing:
      - If the model cannot be loaded (file missing, no internet, etc.),
        this creates and returns a dummy model so that the API remains usable.
    """
    global _model
    if _model is not None:
        return _model

    try:
        _download_model_if_needed()
        _model = joblib.load(config.MODEL_PATH)
        print(f"INFO: Loaded ML model from {config.MODEL_PATH}")
    except Exception as e:
        # Fall back to dummy model instead of crashing locally
        _model = _create_dummy_model(str(e))

    return _model


def date_to_numeric(date_obj: datetime) -> int:
    return (date_obj - config.DATE_MIN).days


def predict_price(feature_dict):
    """
    Predict price using the loaded model (real or dummy).
    """
    model = _load_model()
    df = pd.DataFrame([feature_dict], columns=FEATURE_COLUMNS)
    pred = model.predict(df)[0]
    return float(pred)
