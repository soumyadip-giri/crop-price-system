# KrishiSense – Real-Time ML-Powered Farmer Decision Support System for West Bengal

KrishiSense is an AI-driven web platform that predicts crop prices, fetches live weather, suggests best selling days, and provides agro-climatic advisory for farmers in West Bengal.

Farmers simply select:

- **Crop**
- **Market / District**
- **Intended selling date**
- Enable **GPS** for auto-detecting nearest market & weather

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
```
### ⚙️ Local Setup Guide
- ✅ 1. Clone the Repository
git clone <your_repo_url> KrishiSense
cd KrishiSense

- ✅ 2. Download the ML Model (.pkl)
Open the Google Drive link:
https://drive.google.com/file/d/1XHA5rd3ScFLUdaz4BS6FYOirvwP7Ukhc/view?usp=sharing
Download the file: crop_price_prediction_model_v6_date.pkl

Place it inside:
KrishiSense/backend/ml/crop_price_prediction_model_v6_date.pkl
Make sure the file name matches exactly.

- ✅ 3. Create and Configure .env

Create a file called .env in the project root (same level as backend/ and frontend/):

FLASK_SECRET_KEY=your_random_secret_here
JWT_SECRET=another_random_secret_here

OPENWEATHER_API_KEY=your_openweather_api_key_here

MODEL_PATH=backend/ml/crop_price_prediction_model_v6_date.pkl

MONGO_URI=mongodb://127.0.0.1:27017
MONGO_DB=krishisense


### 🔴 Important:

OPENWEATHER_API_KEY must be a valid key from OpenWeather.

MODEL_PATH must correctly point to the .pkl file you downloaded.

Ensure MongoDB is running locally or update MONGO_URI to your Atlas cluster.

- ✅ 4. Install Backend Dependencies

Open a terminal in the project root and run:

cd backend
pip install -r requirements.txt


(Use a virtual environment if desired.)

- ✅ 5. Run the Backend Server

From the project root or backend/:
python -m backend.app


If using app.py directly:

cd backend
python app.py


By default the backend runs at:

http://127.0.0.1:5000

- ✅ 6. Run the Frontend

There are two options:

Option A – Served by Flask (recommended)
If templates are wired in Flask, just visit:
http://127.0.0.1:5000

Option B – Open HTML directly

- Open the file in browser:
 frontend/templates/index.html


(For API calls to work, ensure API_BASE in frontend/static/js/main.js points to your backend URL.)

### 🔑 OpenWeather Live Weather Setup

Weather may show “offline demo” if:

OPENWEATHER_API_KEY is missing
API key is invalid
Your internet is down
OpenWeather rate limit is exceeded

✅ Double-check:

.env contains a valid OPENWEATHER_API_KEY
Backend is restarted after editing .env
Terminal logs show no weather errors

\
### 🧪 Troubleshooting
❌ Weather shows “offline demo”

Check .env → OPENWEATHER_API_KEY present and correct

Restart backend after updating .env

Confirm server has internet access

❌ “Using DummyModel fallback” or model not loading

Verify MODEL_PATH in .env is correct

Confirm that crop_price_prediction_model_v6_date.pkl exists in backend/ml/

Restart backend

❌ MongoDB not saving history

Ensure MongoDB service is running:

mongod


Or update MONGO_URI to use MongoDB Atlas.

❌ CORS / API errors in browser

Make sure API_BASE in main.js matches backend URL:

Local: const API_BASE = "/api";

Remote: const API_BASE = "https://your-backend-url/api";

### 👨‍🏫 How to Explain in Viva (Short Summary)

“KrishiSense is a real-time farmer decision support system for West Bengal. A farmer just selects crop, market, and date (optionally enabling GPS), and our Flask backend fetches live weather from OpenWeather, combines it with historical prices, agro-climatic zones, and economic indicators, and passes it through a trained RandomForest/XGBoost model. The system predicts modal price, suggests best selling day and market, stores history in MongoDB, and visualizes district-wise price heatmaps and trends through a clean Tailwind + JS frontend.”

### 👨‍💻 Contributors

- **Soumyadip Giri** – ML, Backend, UI/UX

- **Aritra Bose** – Frontend, ML

- **Priyanshu Jana** – Data Analytics

- **Abin Biswas** – Testing & Integration

- **Priyanshu Shekar Pandey** – Analytics & Documentation

### 📜 License

**Academic / non-commercial use only.**
Feel free to reuse components for learning and research with proper acknowledgement.


# crop-price-system - inshort overview to run the website locally

### Download model pkl file as mentioned

model file : https://drive.google.com/file/d/1XHA5rd3ScFLUdaz4BS6FYOirvwP7Ukhc/view?usp=sharing
1. Go to this google drive link
2. Download the crop_price_prediction_model_v6_date.pkl file of the model
3. In this 'ml' folder add the crop_price_prediction_model_v6_date.pkl 


### After pkl file added to ml ,

1.Open new terminal in vs code
2. Install libraries by running the commands: pip install -r requirements.txt
3.Run the webpage: python -m backend.app 
4. Click on this http://127.0.0.1:5000
or
http://127.0.0.1:5000 paste this in the browser.


