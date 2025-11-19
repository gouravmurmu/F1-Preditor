import os
import sys
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import pickle
import pandas as pd

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("f1_api")

app = FastAPI(title="F1 2026 Prediction API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PREDICTOR CLASS (Embedded for robustness) ---
class F1Predictor:
    def __init__(self, model_path, features_path):
        self.model_path = model_path
        self.features_path = features_path
        self.model = None
        self.history_df = None
        self.load_resources()

    def load_resources(self):
        logger.info(f"Loading model from {self.model_path}")
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            logger.error(f"Model not found at {self.model_path}")
            raise FileNotFoundError(f"Model not found at {self.model_path}")
            
        logger.info(f"Loading features from {self.features_path}")
        if os.path.exists(self.features_path):
            self.history_df = pd.read_csv(self.features_path)
        else:
            logger.error(f"Features not found at {self.features_path}")
            raise FileNotFoundError(f"Features not found at {self.features_path}")

    def get_drivers(self):
        return sorted(self.history_df['driverId'].unique().tolist())

    def get_constructors(self):
        return sorted(self.history_df['constructorId'].unique().tolist())

    def get_locations(self):
        return sorted(self.history_df['Location'].unique().tolist())

    def predict(self, race_input):
        # Preprocess
        input_df = pd.DataFrame(race_input)
        
        # Lookup stats
        last_driver_stats = self.history_df.sort_values('year').groupby('driverId').last()
        last_constructor_stats = self.history_df.sort_values('year').groupby('constructorId').last()
        
        input_df['driver_win_rate'] = input_df['driverId'].map(last_driver_stats['driver_win_rate']).fillna(0)
        input_df['driver_recent_form'] = input_df['driverId'].map(last_driver_stats['driver_recent_form']).fillna(20)
        input_df['constructor_win_rate'] = input_df['constructorId'].map(last_constructor_stats['constructor_win_rate']).fillna(0)
        input_df['constructor_recent_points'] = input_df['constructorId'].map(last_constructor_stats['constructor_recent_points']).fillna(0)
        
        # Mappings
        loc_map = dict(zip(self.history_df['Location'], self.history_df['location_id']))
        driver_map = dict(zip(self.history_df['driverId'], self.history_df['driver_id_enc']))
        const_map = dict(zip(self.history_df['constructorId'], self.history_df['constructor_id_enc']))
        
        input_df['location_id'] = input_df['Location'].map(loc_map).fillna(-1)
        input_df['driver_id_enc'] = input_df['driverId'].map(driver_map).fillna(-1)
        input_df['constructor_id_enc'] = input_df['constructorId'].map(const_map).fillna(-1)
        
        features = [
            'grid', 'driver_win_rate', 'driver_recent_form',
            'constructor_win_rate', 'constructor_recent_points',
            'location_id', 'driver_id_enc', 'constructor_id_enc'
        ]
        
        X = input_df[features]
        probs = self.model.predict_proba(X)[:, 1]
        
        results = []
        for i, prob in enumerate(probs):
            results.append({
                'driverId': race_input[i]['driverId'],
                'win_probability': float(prob)
            })
        results.sort(key=lambda x: x['win_probability'], reverse=True)
        return results

# --- INITIALIZATION ---
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "src", "models", "xgb_winner_model.pkl")
features_path = os.path.join(base_dir, "data", "features", "final_features.csv")

predictor = None
try:
    predictor = F1Predictor(model_path, features_path)
    logger.info("Predictor initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize predictor: {e}")
    traceback.print_exc()

# --- MODELS ---
class DriverInput(BaseModel):
    driverId: str
    constructorId: str
    grid: int
    Location: str

class PredictionOutput(BaseModel):
    driverId: str
    win_probability: float

# --- HTML FRONTEND ---
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>F1 2026 Race Predictor</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #15151e; color: #f0f0f0; }
        h1 { color: #e10600; text-align: center; font-style: italic; }
        .card { background: #1f1f2e; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 20px; border: 1px solid #333; }
        h2 { color: #fff; border-bottom: 2px solid #e10600; padding-bottom: 10px; margin-top: 0; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #ccc; }
        select, input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #444; border-radius: 6px; background: #2a2a3d; color: white; font-size: 14px; }
        button { background-color: #e10600; color: white; border: none; padding: 12px 25px; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; transition: background 0.2s; }
        button:hover { background-color: #ff1e1e; }
        .driver-row { display: flex; gap: 15px; align-items: flex-end; background: #252535; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; }
        .driver-row > div { flex: 1; }
        .remove-btn { background: #444; width: auto; padding: 12px 15px; }
        .remove-btn:hover { background: #666; }
        #results { margin-top: 30px; }
        .result-item { padding: 15px; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; font-size: 18px; }
        .result-item:first-child { font-weight: bold; background-color: rgba(225, 6, 0, 0.1); border-radius: 6px; border: 1px solid #e10600; }
        .prob-bar-bg { width: 200px; height: 10px; background: #333; border-radius: 5px; overflow: hidden; margin-left: 15px; }
        .prob-bar-fill { height: 100%; background: #e10600; }
    </style>
</head>
<body>
    <h1>F1 2026 PREDICTOR</h1>
    
    <div class="card">
        <h2>Race Settings</h2>
        <label for="location">Circuit / Location</label>
        <select id="location"></select>
    </div>

    <div class="card">
        <h2>Starting Grid</h2>
        <div id="drivers-container"></div>
        <button onclick="addDriverRow()">+ Add Driver</button>
    </div>

    <button onclick="predict()" style="width: 100%; font-size: 18px; padding: 15px;">PREDICT RACE WINNER</button>

    <div id="results" class="card" style="display: none;">
        <h2>Prediction Results</h2>
        <div id="results-list"></div>
    </div>

    <script>
        let driversList = [];
        let constructorsList = [];

        async function fetchData() {
            try {
                const [driversRes, constructorsRes, locationsRes] = await Promise.all([
                    fetch('/drivers'),
                    fetch('/constructors'),
                    fetch('/locations')
                ]);

                driversList = await driversRes.json();
                constructorsList = await constructorsRes.json();
                const locations = await locationsRes.json();

                const locSelect = document.getElementById('location');
                locations.forEach(loc => {
                    const opt = document.createElement('option');
                    opt.value = loc;
                    opt.textContent = loc;
                    locSelect.appendChild(opt);
                });

                addDriverRow();
                addDriverRow();
            } catch (error) {
                console.error('Error fetching data:', error);
                alert('Failed to load data. Is the API running?');
            }
        }

        function addDriverRow() {
            const container = document.getElementById('drivers-container');
            const row = document.createElement('div');
            row.className = 'driver-row';
            
            row.innerHTML = `
                <div>
                    <label>Driver</label>
                    <select class="driver-select">
                        ${driversList.map(d => `<option value="${d}">${d}</option>`).join('')}
                    </select>
                </div>
                <div>
                    <label>Constructor</label>
                    <select class="constructor-select">
                        ${constructorsList.map(c => `<option value="${c}">${c}</option>`).join('')}
                    </select>
                </div>
                <div style="flex: 0.5;">
                    <label>Grid</label>
                    <input type="number" class="grid-input" min="1" max="20" value="1">
                </div>
                <button class="remove-btn" onclick="this.parentElement.remove()">✕</button>
            `;
            container.appendChild(row);
        }

        async function predict() {
            const location = document.getElementById('location').value;
            const rows = document.querySelectorAll('.driver-row');
            const payload = [];

            rows.forEach(row => {
                payload.push({
                    driverId: row.querySelector('.driver-select').value,
                    constructorId: row.querySelector('.constructor-select').value,
                    grid: parseInt(row.querySelector('.grid-input').value),
                    Location: location
                });
            });

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) throw new Error(await response.text());
                
                const results = await response.json();
                displayResults(results);
            } catch (error) {
                console.error('Error predicting:', error);
                alert('Prediction failed: ' + error.message);
            }
        }

        function displayResults(results) {
            const container = document.getElementById('results-list');
            const resultsDiv = document.getElementById('results');
            container.innerHTML = '';
            resultsDiv.style.display = 'block';

            results.forEach((res, index) => {
                const prob = (res.win_probability * 100).toFixed(1);
                const div = document.createElement('div');
                div.className = 'result-item';
                div.innerHTML = `
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="color:#888; width:20px;">${index + 1}.</span>
                        <span>${res.driverId}</span>
                    </div>
                    <div style="display:flex; align-items:center;">
                        <span>${prob}%</span>
                        <div class="prob-bar-bg">
                            <div class="prob-bar-fill" style="width: ${prob}%"></div>
                        </div>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        fetchData();
    </script>
</body>
</html>
"""

# --- ENDPOINTS ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return html_content

@app.get("/drivers")
def get_drivers():
    if not predictor: raise HTTPException(500, "Model not initialized")
    return predictor.get_drivers()

@app.get("/constructors")
def get_constructors():
    if not predictor: raise HTTPException(500, "Model not initialized")
    return predictor.get_constructors()

@app.get("/locations")
def get_locations():
    if not predictor: raise HTTPException(500, "Model not initialized")
    return predictor.get_locations()

@app.post("/predict", response_model=List[PredictionOutput])
def predict_race(drivers: List[DriverInput]):
    if not predictor: raise HTTPException(500, "Model not initialized")
    try:
        race_input = [d.dict() for d in drivers]
        return predictor.predict(race_input)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    print(f"Starting F1 API on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
