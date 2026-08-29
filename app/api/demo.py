from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RiskScore, Alert

router = APIRouter()

SCENARIOS = {
    "normal": [
        {"zone_id": "MEG_042", "score": 15.0, "level": "LOW", "rainfall_24hr": 12.0, "soil_moisture": 0.32, "ground_displacement": 0.1, "seismic_activity": 0.02, "ndvi": 0.71, "confidence": 0.88, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "SIK_017", "score": 15.0, "level": "LOW", "rainfall_24hr": 8.5, "soil_moisture": 0.28, "ground_displacement": 0.2, "seismic_activity": 0.05, "ndvi": 0.65, "confidence": 0.82, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "MAN_031", "score": 45.0, "level": "MODERATE", "rainfall_24hr": 35.0, "soil_moisture": 0.55, "ground_displacement": 1.2, "seismic_activity": 0.10, "ndvi": 0.48, "confidence": 0.85, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "ARU_008", "score": 35.0, "level": "MODERATE", "rainfall_24hr": 28.0, "soil_moisture": 0.45, "ground_displacement": 0.8, "seismic_activity": 0.08, "ndvi": 0.55, "confidence": 0.83, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "MIZ_022", "score": 40.0, "level": "MODERATE", "rainfall_24hr": 32.0, "soil_moisture": 0.50, "ground_displacement": 1.0, "seismic_activity": 0.09, "ndvi": 0.52, "confidence": 0.84, "satellite_status": "fresh", "sensor_status": "online"},
    ],
    "warning": [
        {"zone_id": "MEG_042", "score": 72.0, "level": "HIGH", "rainfall_24hr": 65.0, "soil_moisture": 0.75, "ground_displacement": 2.5, "seismic_activity": 0.15, "ndvi": 0.38, "confidence": 0.91, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "SIK_017", "score": 58.0, "level": "HIGH", "rainfall_24hr": 52.0, "soil_moisture": 0.68, "ground_displacement": 1.8, "seismic_activity": 0.12, "ndvi": 0.42, "confidence": 0.88, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "MAN_031", "score": 95.0, "level": "CRITICAL", "rainfall_24hr": 89.0, "soil_moisture": 0.91, "ground_displacement": 4.2, "seismic_activity": 0.31, "ndvi": 0.21, "confidence": 0.94, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "ARU_008", "score": 71.0, "level": "HIGH", "rainfall_24hr": 54.0, "soil_moisture": 0.72, "ground_displacement": 2.1, "seismic_activity": 0.18, "ndvi": 0.38, "confidence": 0.87, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "MIZ_022", "score": 88.0, "level": "CRITICAL", "rainfall_24hr": 78.0, "soil_moisture": 0.85, "ground_displacement": 3.2, "seismic_activity": 0.20, "ndvi": 0.27, "confidence": 0.92, "satellite_status": "fresh", "sensor_status": "online"},
    ],
    "emergency": [
        {"zone_id": "MEG_042", "score": 91.0, "level": "CRITICAL", "rainfall_24hr": 112.0, "soil_moisture": 0.95, "ground_displacement": 5.1, "seismic_activity": 0.28, "ndvi": 0.15, "confidence": 0.96, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "SIK_017", "score": 85.0, "level": "CRITICAL", "rainfall_24hr": 98.0, "soil_moisture": 0.89, "ground_displacement": 4.5, "seismic_activity": 0.25, "ndvi": 0.18, "confidence": 0.95, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "MAN_031", "score": 99.0, "level": "CRITICAL", "rainfall_24hr": 145.0, "soil_moisture": 0.98, "ground_displacement": 7.8, "seismic_activity": 0.45, "ndvi": 0.08, "confidence": 0.98, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "ARU_008", "score": 94.0, "level": "CRITICAL", "rainfall_24hr": 128.0, "soil_moisture": 0.93, "ground_displacement": 6.2, "seismic_activity": 0.38, "ndvi": 0.11, "confidence": 0.97, "satellite_status": "fresh", "sensor_status": "online"},
        {"zone_id": "MIZ_022", "score": 97.0, "level": "CRITICAL", "rainfall_24hr": 138.0, "soil_moisture": 0.96, "ground_displacement": 7.1, "seismic_activity": 0.42, "ndvi": 0.09, "confidence": 0.97, "satellite_status": "fresh", "sensor_status": "online"},
    ]
}

@router.post("/{scenario}")
def load_scenario(scenario: str, db: Session = Depends(get_db)):
    if scenario not in SCENARIOS:
        return {"error": "Scenario not found. Use: normal, warning, emergency"}
    
    data = SCENARIOS[scenario]
    
    db.query(Alert).delete()
    db.commit()
    
    for d in data:
        new_score = RiskScore(
            zone_id=d["zone_id"], score=d["score"], level=d["level"],
            rainfall_24hr=d["rainfall_24hr"], soil_moisture=d["soil_moisture"],
            ground_displacement=d["ground_displacement"], seismic_activity=d["seismic_activity"],
            ndvi=d["ndvi"], confidence=d["confidence"],
            satellite_status=d["satellite_status"], sensor_status=d["sensor_status"]
        )
        db.add(new_score)
    
    if scenario == "warning":
        db.add(Alert(zone_id="MAN_031", level="CRITICAL", message="CRITICAL: Landslide imminent near Imphal Valley. Evacuate NH-102 immediately."))
        db.add(Alert(zone_id="MIZ_022", level="CRITICAL", message="CRITICAL: Aizawl South high risk. Move to safe zones now."))
    
    if scenario == "emergency":
        db.add(Alert(zone_id="MEG_042", level="CRITICAL", message="EMERGENCY: Cherrapunji North — active landslide detected. All roads closed."))
        db.add(Alert(zone_id="MAN_031", level="CRITICAL", message="EMERGENCY: Imphal Valley — mass movement confirmed. Evacuate immediately."))
        db.add(Alert(zone_id="MIZ_022", level="CRITICAL", message="EMERGENCY: Aizawl South — infrastructure collapse risk. NH-54 blocked."))
        db.add(Alert(zone_id="ARU_008", level="CRITICAL", message="EMERGENCY: Itanagar Hills — all 5 zones CRITICAL. State disaster declared."))
    
    db.commit()
    return {"status": f"Scenario '{scenario}' loaded successfully", "zones_updated": len(data)}
