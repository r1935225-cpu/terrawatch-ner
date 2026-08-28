from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
import app.models
from app.models import Zone, RiskScore, Alert
from app.api import zones, risk, simulator, impact, community, alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Landslide Warning System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(zones.router,      prefix="/api/zones")
app.include_router(risk.router,       prefix="/api/risk")
app.include_router(simulator.router,  prefix="/api/simulator")
app.include_router(impact.router,     prefix="/api/impact")
app.include_router(community.router,  prefix="/api/community")
app.include_router(alerts.router,     prefix="/api/alerts")

@app.get("/")
def root():
    return {"status": "Landslide API is running"}

@app.post("/seed")
def seed_database():
    db = SessionLocal()
    try:
        db.query(Alert).delete()
        db.query(RiskScore).delete()
        db.query(Zone).delete()
        db.commit()

        zones_data = [
            Zone(id="MEG_042", name="Cherrapunji North", state="Meghalaya",
                 district="East Khasi Hills", latitude=25.284, longitude=91.726,
                 slope_degrees=35.2, elevation=1340.0, erosion_class=4,
                 historical_landslide_count=12,
                 geojson='{"type":"Point","coordinates":[91.726,25.284]}'),
            Zone(id="SIK_017", name="Gangtok East", state="Sikkim",
                 district="East Sikkim", latitude=27.339, longitude=88.617,
                 slope_degrees=28.7, elevation=1650.0, erosion_class=3,
                 historical_landslide_count=7,
                 geojson='{"type":"Point","coordinates":[88.617,27.339]}'),
            Zone(id="MAN_031", name="Imphal Valley Slope", state="Manipur",
                 district="Imphal East", latitude=24.817, longitude=93.944,
                 slope_degrees=42.1, elevation=920.0, erosion_class=5,
                 historical_landslide_count=19,
                 geojson='{"type":"Point","coordinates":[93.944,24.817]}'),
            Zone(id="ARU_008", name="Itanagar Hills", state="Arunachal Pradesh",
                 district="Papum Pare", latitude=27.084, longitude=93.608,
                 slope_degrees=38.5, elevation=1100.0, erosion_class=4,
                 historical_landslide_count=9,
                 geojson='{"type":"Point","coordinates":[93.608,27.084]}'),
            Zone(id="MIZ_022", name="Aizawl South", state="Mizoram",
                 district="Aizawl", latitude=23.727, longitude=92.717,
                 slope_degrees=31.9, elevation=1132.0, erosion_class=3,
                 historical_landslide_count=6,
                 geojson='{"type":"Point","coordinates":[92.717,23.727]}'),
        ]

        risk_data = [
            RiskScore(zone_id="MEG_042", score=15.0, level="LOW",
                      rainfall_24hr=12.0, soil_moisture=0.32, ground_displacement=0.1,
                      seismic_activity=0.02, ndvi=0.71, confidence=0.88,
                      satellite_status="fresh", sensor_status="online"),
            RiskScore(zone_id="SIK_017", score=15.0, level="LOW",
                      rainfall_24hr=8.5, soil_moisture=0.28, ground_displacement=0.2,
                      seismic_activity=0.05, ndvi=0.65, confidence=0.82,
                      satellite_status="fresh", sensor_status="online"),
            RiskScore(zone_id="MAN_031", score=95.0, level="CRITICAL",
                      rainfall_24hr=89.0, soil_moisture=0.91, ground_displacement=4.2,
                      seismic_activity=0.31, ndvi=0.21, confidence=0.94,
                      satellite_status="fresh", sensor_status="online"),
            RiskScore(zone_id="ARU_008", score=71.0, level="HIGH",
                      rainfall_24hr=54.0, soil_moisture=0.72, ground_displacement=2.1,
                      seismic_activity=0.18, ndvi=0.38, confidence=0.87,
                      satellite_status="fresh", sensor_status="online"),
            RiskScore(zone_id="MIZ_022", score=91.0, level="CRITICAL",
                      rainfall_24hr=78.0, soil_moisture=0.87, ground_displacement=3.5,
                      seismic_activity=0.22, ndvi=0.25, confidence=0.91,
                      satellite_status="fresh", sensor_status="online"),
        ]

        alerts_data = [
            Alert(zone_id="MAN_031", level="CRITICAL",
                  message="⚠️ CRITICAL: Landslide risk near Imphal Valley Slope. Avoid NH-102."),
            Alert(zone_id="MIZ_022", level="CRITICAL",
                  message="⚠️ CRITICAL: High risk near Aizawl South. Move to safe zones."),
            Alert(zone_id="ARU_008", level="HIGH",
                  message="⚠️ HIGH RISK: Itanagar Hills elevated risk. Avoid hill roads."),
        ]

        db.add_all(zones_data)
        db.add_all(risk_data)
        db.add_all(alerts_data)
        db.commit()
        return {"status": "Database seeded successfully!", "zones": 5, "risk_scores": 5, "alerts": 3}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()