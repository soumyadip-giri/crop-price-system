# backend/config.py
import os
from datetime import datetime

# Only needed for local development; in production (Render etc.) you set env vars
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# backend/ is inside project-root/backend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)  # project root

# ------------------- load .env (local dev only) -------------------
# On local machine, create a .env file in the project root with values like:
#   MONGO_URI=mongodb://localhost:27017/crop_price_db
#   OPENWEATHER_API_KEY=YOUR_KEY_HERE   (optional for real weather)
#   MODEL_PATH=ml/crop_price_prediction_model_v6_date.pkl
#
# If .env or variables are missing, sensible LOCAL defaults are used.
if load_dotenv is not None:
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)

# ------------------- basic environment flags -------------------
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV != "production"

# ------------------- config values -------------------

# Mongo connection
# Local default: mongodb://localhost:27017/crop_price_db
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/crop_price_db")

# JWT config
# In production you should always set JWT_SECRET from env.
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-me")
JWT_ALGO = "HS256"

# OpenWeather API
# For *local offline testing*, this can be empty. The app will fall back to dummy
# weather in that case (see weather_service.py).
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# (Not strictly needed now; kept for compatibility)
OPENWEATHER_BASE_URL = (
    "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}"
)

# Model path (default: project-root/ml/…)
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.join(ROOT_DIR, "ml", "crop_price_prediction_model_v6_date.pkl"),
)

# Where to download model from if local file is missing (optional)
MODEL_URL = os.getenv("MODEL_URL")

# Baseline for DateNumeric
DATE_MIN = datetime(2019, 1, 1)
