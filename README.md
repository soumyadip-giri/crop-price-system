# KrishiSense – Real-Time ML-Powered Farmer Decision Support System for West Bengal

KrishiSense is an AI-driven web platform that predicts crop prices, fetches live weather, suggests best selling days, and provides agro-climatic advisory for farmers in West Bengal.

Farmers simply select:

- **Crop**
- **Market / District**
- **Intended selling date**
- *(Optional)* Enable **GPS** for auto-detecting nearest market & weather

…and the system uses **machine learning**, **OpenWeather live data**, **historical price trends**, and **agro-zone intelligence** to give **actionable insights**, not just numbers.

---

## ⭐ Key Features

### 🔮 ML-Based Crop Price Prediction

- Trained **RandomForest / XGBoost hybrid model**
- Predicts **modal price** for selected crop, market and date
- Provides **confidence range** and **trend direction** (up / down / neutral)
- Suggests **best selling day** in the next few days

### ☁️ Live Weather Integration

- Fully connected to **OpenWeather API**
- Shows:
  - Current temperature, humidity, rainfall, feels-like
  - 5-day aggregated weather forecast
- No offline/demo data – uses live API when configured correctly

### 🌱 Agro Advisory

- Uses agro-climatic zone + weather to:
  - Give **crop suitability hints**
  - Indicate **disease / pest risk** (weather-driven)
  - Warn about **extreme conditions** (heavy rain, heat, etc.)

### 🗺 Nearby Market Comparison

- Compares **nearby markets** based on predicted price
- Highlights **most profitable market** to sell

### 📈 Prediction History & Analytics

- Stores **prediction logs** securely in MongoDB
- Farmer can **enter actual selling price**
- Auto-calculates **profit / loss** against predicted price
- Interactive **price trend chart** using Chart.js

### 🌍 District Heatmap

- Aggregates district-wise prices from last few days
- Renders **heatmap of West Bengal**:
  - Low / Medium / High price zones
  - Shows **Top 5 highest-price districts**

### 🔐 Secure Authentication

- **JWT-based login** system
- Farmer accounts backed by **MongoDB**
- Passwords stored as **hashed values** only

---

## 🧱 Tech Stack

**Frontend**

- HTML, Tailwind CSS
- Vanilla JavaScript
- Chart.js for charts / trend visualization

**Backend**

- Python, Flask (REST APIs)
- scikit-learn, XGBoost (ML)
- MongoDB (users + prediction logs)
- python-dotenv for environment configuration
- OpenWeather API (live weather)

---

## 📁 Project Structure

```text
crop-price-system/
├── backend/
│   ├── app.py                 # Flask entry (also runnable via python -m backend.app)
│   ├── config.py              # Configuration & environment loading
│   ├── services/
│   │   ├── weather_service.py # OpenWeather API integration
│   │   ├── model_service.py   # Load & run ML model
│   │   ├── agro_service.py    # Agro-climatic advisory logic
│   ├── auth_routes.py                  # Auth, JWT, user management
│   ├── prediction_routes                # API route definitions
│   ├── ml/
│   │   └── crop_price_prediction_model_v6_date.pkl  # ML model file (added by user)
│   └── utils/                 # Helpers, common utilities
├── frontend/
│   ├── templates/
│   │   ├── index.html         # Landing page
│   │   ├── dashboard.html     # Farmer dashboard + heatmap
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── about_model.html   # Model description & explainability
│   ├── static/
│   │   ├── js/
│   │   │   └── main.js        # Frontend logic & API calls
│   │   ├── css/
│   │   │   └── custom.css     # Additional styling
│   │   ├── img/
│   │   │   └── team/          # Team images (optional)
│   │   └── video/             # Demo / intro videos (optional)
└── README.md



# crop-price-system

# Download model pkl file as mentioned

model file : https://drive.google.com/file/d/1XHA5rd3ScFLUdaz4BS6FYOirvwP7Ukhc/view?usp=sharing
1. Go to this google drive link
2. Download the crop_price_prediction_model_v6_date.pkl file of the model
3. In this 'ml' folder add the crop_price_prediction_model_v6_date.pkl 


# After pkl file added to ml ,

1.Open new terminal in vs code
2. Install libraries by running the commands: pip install -r requirements.txt
3.Run the webpage: python -m backend.app 
4. Click on this http://127.0.0.1:5000
or
http://127.0.0.1:5000 paste this in the browser.

