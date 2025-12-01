// frontend/static/js/main.js

const API_BASE = "/api";

// ---------------- token helpers ----------------
function getToken() {
  return localStorage.getItem("jwt_token");
}
function setToken(token) {
  localStorage.setItem("jwt_token", token);
}
function clearToken() {
  localStorage.removeItem("jwt_token");
}

// ------------- markets + crops -------------
const MARKETS = [
  { name: "Kolkata",           lat: 22.5726, lon: 88.3639 },
  { name: "Howrah",            lat: 22.5958, lon: 88.2636 },
  { name: "Hooghly",           lat: 22.8960, lon: 88.2470 },
  { name: "Nadia",             lat: 23.4710, lon: 88.5565 },
  { name: "North 24 Parganas", lat: 22.8950, lon: 88.4152 },
  { name: "South 24 Parganas", lat: 22.3560, lon: 88.4313 },
  { name: "Purba Medinipur",   lat: 22.0653, lon: 87.9927 },
  { name: "Paschim Medinipur", lat: 22.4310, lon: 87.3216 },
  { name: "Jhargram",          lat: 22.4500, lon: 86.9830 },
  { name: "Bankura",           lat: 23.2324, lon: 87.0710 },
  { name: "Birbhum",           lat: 23.8400, lon: 87.6200 },
  { name: "Purba Bardhaman",   lat: 23.2320, lon: 87.8610 },
  { name: "Paschim Bardhaman", lat: 23.6840, lon: 87.5560 },
  { name: "Murshidabad",       lat: 24.1750, lon: 88.2800 },
  { name: "Malda",             lat: 25.0108, lon: 88.1411 },
  { name: "Dakshin Dinajpur",  lat: 25.1350, lon: 88.7660 },
  { name: "Uttar Dinajpur",    lat: 25.6300, lon: 88.3000 },
  { name: "Alipurduar",        lat: 26.4916, lon: 89.5270 },
  { name: "Cooch Behar",       lat: 26.3257, lon: 89.4450 },
  { name: "Jalpaiguri",        lat: 26.5435, lon: 88.7205 },
  { name: "Darjeeling",        lat: 27.0410, lon: 88.2663 },
  { name: "Kalimpong",         lat: 27.0680, lon: 88.4710 },
  { name: "Purulia",           lat: 23.3320, lon: 86.3650 },
];

// allowed crops per market (from your mapping table)
const MARKET_CROP_MAP = {
  "Purba Medinipur": ["Oilseeds", "Potato", "Rice", "Vegetables"],
  "Darjeeling": ["Maize", "Tea"],
  "Kalimpong": ["Tea"],
  "Dakshin Dinajpur": ["Pulses", "Rice", "Wheat"],
  "Howrah": ["Banana", "Rice", "Vegetables"],
  "Kolkata": ["Banana", "Rice", "Vegetables"],
  "Malda": ["Litchi", "Mango", "Rice", "Sugarcane", "Wheat"],
  "Uttar Dinajpur": ["Pineapple", "Rice", "Wheat"],
  "Hooghly": ["Jute", "Potato", "Rice", "Vegetables"],
  "Murshidabad": ["Jute", "Mango", "Oilseeds", "Rice", "Sugarcane", "Wheat"],
  "Nadia": ["Jute", "Mango", "Oilseeds", "Pulses", "Rice"],
  "North 24 Parganas": ["Jute", "Rice", "Vegetables"],
  "South 24 Parganas": ["Banana", "Potato", "Rice", "Vegetables"],
  "Bankura": ["Oilseeds", "Pulses"],
  "Jhargram": ["Oilseeds", "Pulses"],
  "Paschim Medinipur": ["Oilseeds", "Potato", "Rice", "Vegetables"],
  "Purulia": ["Maize", "Oilseeds", "Pulses"],
  "Alipurduar": ["Maize", "Tea"],
  "Cooch Behar": ["Jute", "Maize", "Pineapple", "Tea"],
  "Jalpaiguri": ["Maize", "Pineapple", "Tea"],
  "Birbhum": ["Oilseeds", "Pulses", "Rice"],
  "Paschim Bardhaman": ["Oilseeds", "Potato", "Rice", "Wheat"],
  "Purba Bardhaman": ["Oilseeds", "Potato", "Rice", "Wheat"],
};

// NEW: all unique crops across all markets (for crop dropdown)
const ALL_CROPS = Array.from(
  new Set(Object.values(MARKET_CROP_MAP).flat())
).sort();

// ---- helpers ----
function haversine(lat1, lon1, lat2, lon2) {
  const toRad = (x) => (x * Math.PI) / 180;
  const R = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function findNearestMarket(lat, lon) {
  let best = null;
  let bestDist = Infinity;
  for (const m of MARKETS) {
    const d = haversine(lat, lon, m.lat, m.lon);
    if (d < bestDist) {
      bestDist = d;
      best = m;
    }
  }
  return best;
}

// -------- global state for history chart --------
let historyData = [];
let historyChart = null;

// -------------- on load --------------
document.addEventListener("DOMContentLoaded", () => {
  const navLogin = document.getElementById("nav-login");
  const navLogout = document.getElementById("nav-logout");
  if (navLogin && navLogout) {
    const token = getToken();
    if (token) {
      navLogin.classList.add("hidden");
      navLogout.classList.remove("hidden");
    } else {
      navLogin.classList.remove("hidden");
      navLogout.classList.add("hidden");
    }
    navLogout.addEventListener("click", () => {
      clearToken();
      window.location.href = "/login";
    });
  }

  initAuthForms();
  initPrediction();
  initHeatmap();
});

// ---------- auth ----------
function initAuthForms() {
  const regForm = document.getElementById("register-form");
  if (regForm) {
    regForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(regForm);
      const payload = Object.fromEntries(fd.entries());
      const msg = document.getElementById("register-message");
      msg.textContent = "Registering...";
      try {
        const res = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) {
          msg.textContent = data.error || "Registration failed";
          msg.className = "text-red-400 text-sm text-center mt-2";
        } else {
          msg.textContent = "Registered! Redirecting to login...";
          msg.className = "text-emerald-400 text-sm text-center mt-2";
          setTimeout(() => (window.location.href = "/login"), 1200);
        }
      } catch (err) {
        msg.textContent = "Network error";
        msg.className = "text-red-400 text-sm text-center mt-2";
      }
    });
  }

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(loginForm);
      const payload = Object.fromEntries(fd.entries());
      const msg = document.getElementById("login-message");
      msg.textContent = "Logging in...";
      msg.className = "text-slate-300 text-sm text-center mt-2";

      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        // Read raw text first (could be JSON or error HTML)
        const rawText = await res.text();
        let data = {};
        try {
          data = rawText ? JSON.parse(rawText) : {};
        } catch (err) {
          console.error("Login response is not JSON. Raw:", rawText);
          data = {};
        }

        if (!res.ok) {
          // error from backend (401/500/etc.)
          msg.textContent =
            data.error || `Login failed (status ${res.status})`;
          msg.className = "text-red-400 text-sm text-center mt-2";
          return;
        }

        // success
        setToken(data.token);
        msg.textContent = "Success! Redirecting…";
        msg.className = "text-emerald-400 text-sm text-center mt-2";
        setTimeout(() => (window.location.href = "/dashboard"), 800);
      } catch (err) {
        console.error("Login fetch error:", err);
        msg.textContent = "Network error while contacting server";
        msg.className = "text-red-400 text-sm text-center mt-2";
      }
    });
  }
}

// ---------- prediction & agro UI ----------
function initPrediction() {
  const form = document.getElementById("predict-form");
  if (!form) return;

  // require login for dashboard
  if (!getToken()) {
    window.location.href = "/login";
    return;
  }

  const useGps = document.getElementById("use-gps");
  const marketSelect = document.getElementById("market-select");
  const cropSelect = document.getElementById("crop-select");
  const marketHint = document.getElementById("market-crop-hint");
  let currentCoords = { lat: null, lon: null };

  // --- populate crop dropdown with ALL crops ---
  if (cropSelect) {
    cropSelect.innerHTML = "";
    const def = document.createElement("option");
    def.value = "";
    def.disabled = true;
    def.selected = true;
    def.textContent = "Select crop";
    cropSelect.appendChild(def);

    ALL_CROPS.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c;
      opt.textContent = c;
      cropSelect.appendChild(opt);
    });
  }

  // --- helper: update hint for chosen market ---
  function updateMarketHint(marketName) {
    if (!marketHint) return;
    const allowed = MARKET_CROP_MAP[marketName];
    if (allowed && allowed.length) {
      marketHint.textContent = `Typical crops for ${marketName}: ${allowed.join(", ")}`;
    } else {
      marketHint.textContent = "";
    }
  }

  if (marketSelect) {
    updateMarketHint(marketSelect.value);
    marketSelect.addEventListener("change", () => {
      updateMarketHint(marketSelect.value);
    });
  }

  // GPS auto-detect
  if (useGps) {
    useGps.addEventListener("change", () => {
      if (useGps.checked) {
        if (!navigator.geolocation) {
          alert("Geolocation not supported by this browser.");
          useGps.checked = false;
          return;
        }
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            currentCoords.lat = pos.coords.latitude;
            currentCoords.lon = pos.coords.longitude;
            const nearest = findNearestMarket(currentCoords.lat, currentCoords.lon);
            if (nearest && marketSelect) {
              marketSelect.value = nearest.name;
              updateMarketHint(nearest.name);
            }
          },
          (err) => {
            alert("Unable to get location: " + err.message);
            useGps.checked = false;
          }
        );
      } else {
        currentCoords = { lat: null, lon: null };
      }
    });
  }

  // submit handler
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());

    // ---- NEW: crop vs market validation ----
    const selMarket = payload.market;
    const selCrop = payload.crop;
    const allowed = MARKET_CROP_MAP[selMarket];

    if (allowed && selCrop && !allowed.includes(selCrop)) {
      alert(
        `The selected crop "${selCrop}" is not typically grown in ${selMarket}.\n\n` +
        `For ${selMarket}, please choose one of:\n` +
        `• ${allowed.join(", ")}`
      );
      return; // stop here; do not call prediction API
    }
    // ---------------------------------------

    if (useGps && useGps.checked) {
      if (!currentCoords.lat) {
        alert("Location not yet available. Please wait a moment and try again.");
        return;
      }
      payload.lat = currentCoords.lat;
      payload.lon = currentCoords.lon;
    } else {
      payload.lat = 23.5;
      payload.lon = 88.1;
    }

    const token = getToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (res.status === 401) {
        clearToken();
        alert("Session expired. Please login again.");
        window.location.href = "/login";
        return;
      }

      const data = await res.json();
      if (!res.ok) {
        const msg =
          (data.error || "Prediction failed") +
          (data.detail ? `\n\nDetails: ${data.detail}` : "");
        alert(msg);
        return;
      }
      renderPrediction(data);
      loadHistory();
      loadHeatmap();
    } catch (err) {
      alert("Network error");
    }
  });

  loadHistory();
  loadHeatmap();
}

function renderPrediction(data) {
  const container = document.getElementById("prediction-result");
  container.classList.remove("hidden");

  const price = data.predictedPrice;
  document.getElementById("predicted-price").textContent = price.toFixed(2);

  const conf = `${data.confidenceLower.toFixed(2)} – ${data.confidenceUpper.toFixed(2)}`;
  document.getElementById("confidence-range").textContent = conf;

  const trendIcon = document.getElementById("trend-icon");
  trendIcon.textContent = data.trendDirection === "up" ? "🔺" :
                          data.trendDirection === "down" ? "🔻" : "➖";

  const bestDayText = document.getElementById("best-day-text");
  if (data.bestDay) {
    bestDayText.textContent =
      `Best selling day in next 3 days: ${data.bestDay.label} (${data.bestDay.price.toFixed(2)} ₹/kg)`;
  } else {
    bestDayText.textContent = "";
  }

  document.getElementById("advice-text").textContent = data.advice;

  const w = data.weather || {};

  const tempEl = document.getElementById("weather-temp");
  const condEl = document.getElementById("weather-condition");
  const humEl = document.getElementById("weather-humidity");
  const rainEl = document.getElementById("weather-rain");
  const feelsEl = document.getElementById("weather-feels");

  const tempVal =
    w.temp_c != null && w.temp_c.toFixed ? w.temp_c.toFixed(1) : (w.temp_c ?? "--");
  const feelsVal =
    w.feels_like_c != null && w.feels_like_c.toFixed
      ? w.feels_like_c.toFixed(1)
      : tempVal;

  if (tempEl) tempEl.textContent = tempVal;
  if (condEl) condEl.textContent = w.description || "—";
  if (humEl) humEl.textContent = (w.humidity != null ? w.humidity : "--") + " %";
  if (rainEl)
    rainEl.textContent =
      (w.rainfall_mm != null ? w.rainfall_mm.toFixed(1) : "0.0") + " mm";
  if (feelsEl) feelsEl.textContent = feelsVal + " °C";

  const fList = document.getElementById("forecast-info");
  fList.innerHTML = "";
  (data.forecastWeather || []).forEach((d) => {
    const li = document.createElement("li");
    li.textContent = `${d.date}: ${d.temp_c.toFixed(
      1
    )} °C, rain ${(d.rainfall_mm || 0).toFixed(1)} mm`;
    fList.appendChild(li);
  });

  // Agro insights
  const agro = data.agroInsights || {};
  const suitBadge = document.getElementById("suitability-badge");
  suitBadge.textContent = agro.suitabilityLevel || "";
  suitBadge.classList.remove("border-emerald-400", "border-yellow-300", "border-red-400");
  if (agro.suitabilityLevel === "ideal") {
    suitBadge.classList.add("border-emerald-400", "text-emerald-300");
  } else if (agro.suitabilityLevel === "moderate") {
    suitBadge.classList.add("border-yellow-300", "text-yellow-200");
  } else if (agro.suitabilityLevel === "stressful") {
    suitBadge.classList.add("border-red-400", "text-red-300");
  }

  document.getElementById("suitability-text").textContent = agro.suitabilityText || "";
  document.getElementById("disease-risk").textContent = agro.diseaseRisk || "";
  document.getElementById("extreme-warning").textContent = agro.extremeWarning || "";

  // Alternative markets
  const altList = document.getElementById("alternative-markets");
  altList.innerHTML = "";
  (data.alternativeMarkets || []).forEach((m) => {
    const li = document.createElement("li");
    li.innerHTML = `<span class="font-semibold">${m.market}</span> – ${m.price.toFixed(2)} ₹/kg`;
    altList.appendChild(li);
  });
  if (!data.alternativeMarkets || !data.alternativeMarkets.length) {
    altList.innerHTML = `<li class="text-slate-400">Nearby comparison not available.</li>`;
  }

  // Feature summary
  const fsList = document.getElementById("feature-summary");
  fsList.innerHTML = "";
  (data.featureImportanceSummary || []).forEach((txt) => {
    const li = document.createElement("li");
    li.textContent = txt;
    fsList.appendChild(li);
  });
}

// ---------- history + profit/loss + chart ----------
async function loadHistory() {
  const box = document.getElementById("history-list");
  if (!box || !getToken()) return;
  box.innerHTML = "<p class='text-slate-300 text-xs'>Loading...</p>";
  try {
    const res = await fetch(`${API_BASE}/predict/history`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    if (res.status === 401) {
      clearToken();
      window.location.href = "/login";
      return;
    }

    const data = await res.json();
    if (!res.ok) {
      box.innerHTML =
        "<p class='text-red-400 text-xs'>Failed to load history</p>";
      return;
    }
    historyData = data;
    if (!data.length) {
      box.innerHTML =
        "<p class='text-slate-300 text-xs'>No predictions yet.</p>";
      renderHistoryChart();
      return;
    }
    box.innerHTML = "";
    data.forEach((p) => {
      const div = document.createElement("div");
      div.className = "border border-slate-700 rounded-2xl px-3 py-2 space-y-1";
      div.dataset.id = p.id;

      let actualHtml = "";
      if (p.actualPrice != null) {
        const diff = p.priceDiff || 0;
        const cls =
          diff > 0 ? "text-emerald-400" : diff < 0 ? "text-red-400" : "text-slate-200";
        const sign = diff > 0 ? "+" : "";
        actualHtml = `
          <div class="flex justify-between text-[11px]">
            <span>Actual: ${p.actualPrice.toFixed(2)} ₹/kg</span>
            <span class="${cls}">Diff: ${sign}${diff.toFixed(2)} ₹/kg</span>
          </div>`;
      } else {
        actualHtml = `
          <form class="flex items-center gap-1 text-[11px] mt-1 history-actual-form">
            <input type="number" step="0.01" min="0"
                   placeholder="Actual price"
                   class="w-24 px-1 py-0.5 rounded bg-slate-800 border border-slate-600">
            <button type="submit"
                    class="px-2 py-0.5 rounded bg-emerald-500 text-slate-900 font-semibold">
              Save
            </button>
          </form>`;
      }

      div.innerHTML = `
        <div class="flex justify-between items-center text-[11px]">
          <div>
            <span class="font-semibold">${p.crop} • ${p.market}</span><br>
            <span class="text-slate-400">${new Date(
              p.createdAt
            ).toLocaleDateString()}</span>
          </div>
          <button type="button"
                  class="history-delete text-[10px] px-2 py-0.5 rounded-full bg-slate-800 hover:bg-red-500 hover:text-slate-900 border border-slate-600">
            Delete
          </button>
        </div>
        <div class="mt-1 text-[11px]">
          Predicted: <span class="text-emerald-400 font-semibold">${p.predictedPrice.toFixed(
            2
          )} ₹/kg</span>
        </div>
        ${actualHtml}
      `;
      box.appendChild(div);
    });

    // attach listeners for actual-price forms
    box.querySelectorAll(".history-actual-form").forEach((form) => {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const card = form.closest("[data-id]");
        const id = card.dataset.id;
        const input = form.querySelector("input[type='number']");
        const val = parseFloat(input.value);
        if (!val || val <= 0) {
          alert("Enter a valid actual price.");
          return;
        }
        try {
          const res2 = await fetch(`${API_BASE}/predict/actual`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${getToken()}`,
            },
            body: JSON.stringify({ predictionId: id, actualPrice: val }),
          });
          if (res2.status === 401) {
            clearToken();
            window.location.href = "/login";
            return;
          }
          const d2 = await res2.json();
          if (!res2.ok) {
            alert(d2.error || "Failed to save actual price");
            return;
          }
          loadHistory();
        } catch (err) {
          alert("Network error");
        }
      });
    });

    // attach listeners for delete buttons
    box.querySelectorAll(".history-delete").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const card = btn.closest("[data-id]");
        const id = card.dataset.id;
        const ok = confirm("Delete this prediction entry?");
        if (!ok) return;

        try {
          const resDel = await fetch(`${API_BASE}/predict/${id}`, {
            method: "DELETE",
            headers: {
              Authorization: `Bearer ${getToken()}`,
            },
          });

          if (resDel.status === 401) {
            clearToken();
            window.location.href = "/login";
            return;
          }

          const dDel = await resDel.json();
          if (!resDel.ok) {
            alert(dDel.error || "Failed to delete prediction");
            return;
          }

          // reload history and heatmap after deletion
          loadHistory();
          loadHeatmap();
        } catch (err) {
          alert("Network error while deleting prediction.");
        }
      });
    });

    populateHistoryFilters();
    renderHistoryChart();
  } catch (err) {
    box.innerHTML =
      "<p class='text-red-400 text-xs'>Network error</p>";
  }
}

function populateHistoryFilters() {
  const cropSel = document.getElementById("history-filter-crop");
  const marketSel = document.getElementById("history-filter-market");
  if (!cropSel || !marketSel) return;
  const crops = new Set();
  const markets = new Set();
  historyData.forEach((p) => {
    crops.add(p.crop);
    markets.add(p.market);
  });

  cropSel.innerHTML = '<option value="">All Crops</option>';
  markets.forEach(() => {}); // dummy
  crops.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    cropSel.appendChild(opt);
  });

  marketSel.innerHTML = '<option value="">All Markets</option>';
  markets.clear();
  historyData.forEach((p) => markets.add(p.market));
  markets.forEach((m) => {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    marketSel.appendChild(opt);
  });

  cropSel.onchange = renderHistoryChart;
  marketSel.onchange = renderHistoryChart;
}

function renderHistoryChart() {
  const canvas = document.getElementById("history-chart");
  if (!canvas || !historyData.length) {
    if (historyChart) {
      historyChart.destroy();
      historyChart = null;
    }
    return;
  }
  const cropSel = document.getElementById("history-filter-crop");
  const marketSel = document.getElementById("history-filter-market");
  const cropFilter = cropSel ? cropSel.value : "";
  const marketFilter = marketSel ? marketSel.value : "";

  let data = historyData.slice().reverse(); // oldest first
  if (cropFilter) data = data.filter((p) => p.crop === cropFilter);
  if (marketFilter) data = data.filter((p) => p.market === marketFilter);

  const labels = data.map((p) =>
    new Date(p.createdAt).toLocaleDateString()
  );
  const prices = data.map((p) => p.predictedPrice);

  const ctx = canvas.getContext("2d");
  if (historyChart) {
    historyChart.destroy();
  }
  historyChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Predicted price (₹/kg)",
          data: prices,
          tension: 0.3,
        },
      ],
    },
    options: {
      scales: {
        x: { ticks: { autoSkip: true, maxTicksLimit: 6 } },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
}

// ---------- heatmap + top 5 ----------
function initHeatmap() {
  const select = document.getElementById("heatmap-crop");
  if (!select) return;
  select.addEventListener("change", loadHeatmap);
}

async function loadHeatmap() {
  const grid = document.getElementById("heatmap-grid");
  const select = document.getElementById("heatmap-crop");
  const topEl = document.getElementById("top5-table");
  if (!grid || !select || !getToken()) return;
  grid.innerHTML = "<p class='text-slate-300 text-xs'>Loading...</p>";
  if (topEl) topEl.innerHTML = "";

  const crop = select.value;
  const url = crop
    ? `${API_BASE}/heatmap/latest?crop=${encodeURIComponent(crop)}`
    : `${API_BASE}/heatmap/latest`;
  try {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    if (res.status === 401) {
      clearToken();
      window.location.href = "/login";
      return;
    }

    const data = await res.json();
    if (!res.ok) {
      grid.innerHTML =
        "<p class='text-red-400 text-xs'>Failed to load data</p>";
      return;
    }
    if (!data.length) {
      grid.innerHTML =
        "<p class='text-slate-300 text-xs'>No data yet. Make some predictions.</p>";
      return;
    }

    // Top 5 table
    if (topEl) {
      const top = [...data].sort((a, b) => b.avgPrice - a.avgPrice).slice(0, 5);
      let html = "<div class='mb-1 font-semibold'>Top 5 districts (avg price)</div>";
      html += "<div class='space-y-1'>";
      top.forEach((d) => {
        html += `<div class="flex justify-between">
          <span>${d.market} (${d.crop})</span>
          <span class="text-emerald-400 font-semibold">${d.avgPrice.toFixed(2)} ₹/kg</span>
        </div>`;
      });
      html += "</div>";
      topEl.innerHTML = html;
    }

    // Cards grid
    grid.innerHTML = "";
    data.forEach((d) => {
      const div = document.createElement("div");
      div.className =
        "rounded-2xl px-3 py-2 border border-slate-700 bg-slate-800/70";
      const price = d.avgPrice;
      let levelClass = "text-slate-200";
      if (price >= 40) levelClass = "text-emerald-400";
      else if (price <= 20) levelClass = "text-yellow-300";
      div.innerHTML = `
        <div class="text-xs font-semibold">${d.market}</div>
        <div class="text-[11px] text-slate-400">${d.crop}</div>
        <div class="mt-1 text-sm ${levelClass} font-bold">${price.toFixed(
          2
        )} ₹/kg</div>
      `;
      grid.appendChild(div);
    });
  } catch (err) {
    grid.innerHTML =
      "<p class='text-red-400 text-xs'>Network error</p>";
  }
}
