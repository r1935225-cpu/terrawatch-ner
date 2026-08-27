from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import RiskScore

router = APIRouter()

class SimulatorInput(BaseModel):
    zone_id: str
    delta_rainfall: float = 0
    delta_soil_moisture: float = 0
    delta_ground_movement: float = 0

def calculate_score(rainfall, soil_moisture, ground_displacement, seismic, ndvi):
    score = (
        (rainfall * 0.35) +
        (soil_moisture * 100 * 0.25) +
        (ground_displacement * 10 * 0.20) +
        (seismic * 100 * 0.10) +
        ((1 - ndvi) * 100 * 0.10)
    )
    return round(min(score, 100), 1)

def score_to_level(score):
    if score < 30:   return "LOW"
    elif score < 60: return "MODERATE"
    elif score < 80: return "HIGH"
    else:            return "CRITICAL"

@router.post("/run")
def run_simulator(data: SimulatorInput, db: Session = Depends(get_db)):
    latest = db.query(RiskScore)\
               .filter(RiskScore.zone_id == data.zone_id)\
               .order_by(RiskScore.timestamp.desc())\
               .first()

    if not latest:
        return {"error": "Zone not found"}

    # Original score
    original_score = calculate_score(
        latest.rainfall_24hr,
        latest.soil_moisture,
        latest.ground_displacement,
        latest.seismic_activity,
        latest.ndvi
    )

    # Modified score (what-if)
    simulated_score = calculate_score(
        latest.rainfall_24hr + data.delta_rainfall,
        min(latest.soil_moisture + data.delta_soil_moisture, 1.0),
        latest.ground_displacement + data.delta_ground_movement,
        latest.seismic_activity,
        latest.ndvi
    )

    return {
        "zone_id": data.zone_id,
        "original_score": original_score,
        "original_level": score_to_level(original_score),
        "simulated_score": simulated_score,
        "simulated_level": score_to_level(simulated_score),
        "changes": {
            "delta_rainfall": data.delta_rainfall,
            "delta_soil_moisture": data.delta_soil_moisture,
            "delta_ground_movement": data.delta_ground_movement
        }
    }