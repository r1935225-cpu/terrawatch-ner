from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models
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