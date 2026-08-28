from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RiskScore, Zone
from app.services.ml_model import predict_risk, explain_risk
from app.services.weather import get_real_rainfall, get_real_seismic

router = APIRouter()

@router.get("/zone/{zone_id}")
def get_zone_risk(zone_id: str, db: Session = Depends(get_db)):
    latest = db.query(RiskScore)\
               .filter(RiskScore.zone_id == zone_id)\
               .order_by(RiskScore.timestamp.desc())\
               .first()

    if not latest:
        return {"error": "Zone not found"}

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

@router.get("/live/{zone_id}")
def get_live_risk(zone_id: str, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        return {"error": "Zone not found"}

    # Fetch real data
    weather = get_real_rainfall(zone.latitude, zone.longitude)
    seismic = get_real_seismic(zone.latitude, zone.longitude)

    zone_data = {
        "rainfall_24hr": weather["rainfall_24hr"],
        "slope_degrees": zone.slope_degrees,
        "soil_moisture": weather["humidity"] / 100,
        "ground_displacement": 0.5,
        "seismic_activity": seismic,
        "erosion_class": zone.erosion_class,
        "historical_count": zone.historical_landslide_count,
        "ndvi": 0.4,
        "elevation": zone.elevation
    }

    prediction = predict_risk(zone_data)
    breakdown = explain_risk(zone_data)

       # Save to DB — convert numpy types to Python float
    new_score = RiskScore(
        zone_id=zone_id,
        score=float(prediction["score"]),
        level=str(prediction["level"]),
        rainfall_24hr=float(weather["rainfall_24hr"]),
        soil_moisture=float(zone_data["soil_moisture"]),
        ground_displacement=float(0.5),
        seismic_activity=float(seismic),
        ndvi=float(0.4),
        confidence=float(82),
        satellite_status="fresh",
        sensor_status="online"
    )
    db.add(new_score)
    db.commit()

    return {
        "zone_id": zone_id,
        "zone_name": zone.name,
        "weather": weather,
        "seismic_activity": seismic,
        "prediction": prediction,
        "breakdown": breakdown,
        "data_sources": {
            "weather": "OpenWeatherMap API",
            "seismic": "USGS Earthquake API",
            "terrain": "Zone database"
        }
    }