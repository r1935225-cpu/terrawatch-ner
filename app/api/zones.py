from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Zone, RiskScore

router = APIRouter()

@router.get("/all")
def get_all_zones(db: Session = Depends(get_db)):
    zones = db.query(Zone).all()
    result = []
    for zone in zones:
        latest_risk = db.query(RiskScore)\
                        .filter(RiskScore.zone_id == zone.id)\
                        .order_by(RiskScore.timestamp.desc())\
                        .first()
        result.append({
            "id": zone.id,
            "name": zone.name,
            "state": zone.state,
            "district": zone.district,
            "latitude": zone.latitude,
            "longitude": zone.longitude,
            "slope_degrees": zone.slope_degrees,
            "elevation": zone.elevation,
            "risk_score": latest_risk.score if latest_risk else None,
            "risk_level": latest_risk.level if latest_risk else "UNKNOWN"
        })
    return result

@router.post("/seed")
def seed_zones(db: Session = Depends(get_db)):
    # Sample NER zones with realistic data
    sample_zones = [
        Zone(id="MEG_001", name="Cherrapunji North", state="Meghalaya",
             district="East Khasi Hills", latitude=25.28, longitude=91.72,
             slope_degrees=35.2, elevation=1484, erosion_class=4,
             historical_landslide_count=8),
        Zone(id="SIK_001", name="Gangtok East", state="Sikkim",
             district="East Sikkim", latitude=27.33, longitude=88.62,
             slope_degrees=28.5, elevation=1650, erosion_class=3,
             historical_landslide_count=5),
        Zone(id="MAN_001", name="Imphal Valley Slope", state="Manipur",
             district="Imphal East", latitude=24.82, longitude=93.95,
             slope_degrees=22.1, elevation=920, erosion_class=2,
             historical_landslide_count=3),
        Zone(id="ARU_001", name="Itanagar Hills", state="Arunachal Pradesh",
             district="Papum Pare", latitude=27.08, longitude=93.61,
             slope_degrees=31.8, elevation=1100, erosion_class=3,
             historical_landslide_count=6),
        Zone(id="MIZ_001", name="Aizawl South", state="Mizoram",
             district="Aizawl", latitude=23.72, longitude=92.71,
             slope_degrees=38.4, elevation=1132, erosion_class=5,
             historical_landslide_count=12),
    ]

    # Sample risk scores
    sample_risks = [
        RiskScore(zone_id="MEG_001", score=84, level="CRITICAL",
                  rainfall_24hr=142, soil_moisture=0.89, ground_displacement=2.1,
                  seismic_activity=0.3, ndvi=0.31, confidence=87,
                  satellite_status="fresh", sensor_status="online"),
        RiskScore(zone_id="SIK_001", score=62, level="HIGH",
                  rainfall_24hr=98, soil_moisture=0.71, ground_displacement=1.2,
                  seismic_activity=0.5, ndvi=0.42, confidence=79,
                  satellite_status="fresh", sensor_status="online"),
        RiskScore(zone_id="MAN_001", score=38, level="MODERATE",
                  rainfall_24hr=55, soil_moisture=0.52, ground_displacement=0.4,
                  seismic_activity=0.2, ndvi=0.58, confidence=91,
                  satellite_status="fresh", sensor_status="offline"),
        RiskScore(zone_id="ARU_001", score=71, level="HIGH",
                  rainfall_24hr=115, soil_moisture=0.78, ground_displacement=1.8,
                  seismic_activity=0.4, ndvi=0.38, confidence=83,
                  satellite_status="fresh", sensor_status="online"),
        RiskScore(zone_id="MIZ_001", score=91, level="CRITICAL",
                  rainfall_24hr=178, soil_moisture=0.94, ground_displacement=3.2,
                  seismic_activity=0.6, ndvi=0.22, confidence=92,
                  satellite_status="fresh", sensor_status="online"),
    ]

    # Clear existing and insert fresh
    db.query(RiskScore).delete()
    db.query(Zone).delete()
    db.add_all(sample_zones)
    db.commit()
    db.add_all(sample_risks)
    db.commit()

    return {"message": "5 zones seeded successfully"}