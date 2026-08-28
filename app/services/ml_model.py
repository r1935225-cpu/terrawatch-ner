import joblib
import numpy as np
import os

MODEL_PATH = 'ml/model.pkl'
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("ML model loaded successfully")
    else:
        print("No model found — run ml/train.py first")

load_model()

FEATURES = [
    'rainfall_24hr', 'slope_degrees', 'soil_moisture',
    'ground_displacement', 'seismic_activity',
    'erosion_class', 'historical_count',
    'ndvi', 'elevation'
]

def predict_risk(zone_data: dict) -> dict:
    if model is None:
        return fallback_risk(zone_data)

    features = np.array([[
        zone_data.get('rainfall_24hr', 50),
        zone_data.get('slope_degrees', 30),
        zone_data.get('soil_moisture', 0.5),
        zone_data.get('ground_displacement', 0.5),
        zone_data.get('seismic_activity', 0.2),
        zone_data.get('erosion_class', 3),
        zone_data.get('historical_count', 3),
        zone_data.get('ndvi', 0.5),
        zone_data.get('elevation', 1000)
    ]])

    prob = model.predict_proba(features)[0][1]
    return {
        "score": float(round(prob * 100, 1)),
        "level": score_to_level(float(prob * 100)),
        "model": "XGBoost"
    }

def explain_risk(zone_data: dict) -> dict:
    if model is None:
        return {}

    importances = model.feature_importances_
    total = sum(importances)
    return {
        FEATURES[i]: float(round(importances[i] / total * 100, 1))
        for i in range(len(FEATURES))
    }

def score_to_level(score):
    if score < 30:   return "LOW"
    elif score < 60: return "MODERATE"
    elif score < 80: return "HIGH"
    else:            return "CRITICAL"

def fallback_risk(zone_data):
    score = (
        zone_data.get('rainfall_24hr', 0) * 0.35 +
        zone_data.get('slope_degrees', 0) * 0.25 +
        zone_data.get('soil_moisture', 0) * 100 * 0.20 +
        zone_data.get('ground_displacement', 0) * 10 * 0.15 +
        zone_data.get('seismic_activity', 0) * 100 * 0.05
    )
    score = min(round(score, 1), 100)
    return {"score": score, "level": score_to_level(score), "model": "formula"}