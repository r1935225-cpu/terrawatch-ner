from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RiskScore

router = APIRouter()

@router.get("/zone/{zone_id}")
def get_zone_risk(zone_id: str, db: Session = Depends(get_db)):
    # Get latest score
    latest = db.query(RiskScore)\
               .filter(RiskScore.zone_id == zone_id)\
               .order_by(RiskScore.timestamp.desc())\
               .first()

    if not latest:
        return {"error": "Zone not found"}

    # Get last 7 records for momentum
    history = db.query(RiskScore)\
                .filter(RiskScore.zone_id == zone_id)\
                .order_by(RiskScore.timestamp.desc())\
                .limit(7).all()

    scores = [r.score for r in reversed(history)]

    if len(scores) >= 2:
        trend = "accelerating" if scores[-1] > scores[-2] else "improving"
    else:
        trend = "stable"

    return {
        "zone_id": zone_id,
        "current_score": latest.score,
        "level": latest.level,
        "confidence": latest.confidence,
        "satellite_status": latest.satellite_status,
        "sensor_status": latest.sensor_status,
        "momentum": scores,
        "trend": trend,
        "last_updated": latest.timestamp,
        "factors": {
            "rainfall_24hr": latest.rainfall_24hr,
            "soil_moisture": latest.soil_moisture,
            "ground_displacement": latest.ground_displacement,
            "seismic_activity": latest.seismic_activity,
            "ndvi": latest.ndvi
        }
    }

@router.get("/explain/{zone_id}")
def explain_zone_risk(zone_id: str, db: Session = Depends(get_db)):
    latest = db.query(RiskScore)\
               .filter(RiskScore.zone_id == zone_id)\
               .order_by(RiskScore.timestamp.desc())\
               .first()

    if not latest:
        return {"error": "Zone not found"}

    # Calculate contribution percentages
    factors = {
        "Rainfall": latest.rainfall_24hr / 2,
        "Soil Moisture": latest.soil_moisture * 40,
        "Ground Movement": latest.ground_displacement * 15,
        "Seismic Activity": latest.seismic_activity * 20,
        "Vegetation Loss": (1 - latest.ndvi) * 30
    }

    total = sum(factors.values())
    breakdown = {k: round(v / total * 100, 1) for k, v in factors.items()}

    return {
        "zone_id": zone_id,
        "risk_score": latest.score,
        "level": latest.level,
        "breakdown": breakdown
    }

@router.get("/all-levels")
def get_all_risk_levels(db: Session = Depends(get_db)):
    scores = db.query(RiskScore)\
               .order_by(RiskScore.timestamp.desc())\
               .all()

    seen = set()
    result = []
    for s in scores:
        if s.zone_id not in seen:
            seen.add(s.zone_id)
            result.append({
                "zone_id": s.zone_id,
                "score": s.score,
                "level": s.level,
                "confidence": s.confidence
            })
    return result