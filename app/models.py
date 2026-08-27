from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class Zone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True)
    name = Column(String)
    state = Column(String)
    district = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    geojson = Column(Text)
    slope_degrees = Column(Float)
    elevation = Column(Float)
    erosion_class = Column(Integer)
    historical_landslide_count = Column(Integer)

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String)
    score = Column(Float)
    level = Column(String)
    rainfall_24hr = Column(Float)
    soil_moisture = Column(Float)
    ground_displacement = Column(Float)
    seismic_activity = Column(Float)
    ndvi = Column(Float)
    confidence = Column(Float)
    satellite_status = Column(String)
    sensor_status = Column(String)
    timestamp = Column(DateTime, default=func.now())

class CommunityReport(Base):
    __tablename__ = "community_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float)
    longitude = Column(Float)
    observation_type = Column(String)
    description = Column(Text)
    photo_url = Column(String)
    ai_verified = Column(Boolean, default=False)
    status = Column(String, default="pending")
    submitted_at = Column(DateTime, default=func.now())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String)
    level = Column(String)
    message = Column(Text)
    was_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=func.now())