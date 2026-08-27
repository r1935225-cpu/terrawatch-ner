from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CommunityReport
import random

router = APIRouter()

@router.post("/report")
async def submit_report(
    latitude: float = Form(...),
    longitude: float = Form(...),
    observation_type: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    # AI verification simulation
    # In real system: run image classifier here
    valid_types = ["crack", "rockfall", "water_seepage", "ground_movement"]
    is_valid = observation_type in valid_types
    confidence = round(random.uniform(0.75, 0.95), 2)

    report = CommunityReport(
        latitude=latitude,
        longitude=longitude,
        observation_type=observation_type,
        description=description,
        photo_url="no_photo",
        ai_verified=is_valid,
        status="pending"
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Check if multiple reports in same area
    nearby = db.query(CommunityReport)\
               .filter(CommunityReport.status == "pending")\
               .all()

    auto_escalated = len(nearby) >= 3

    return {
        "report_id": f"RPT_{report.id:04d}",
        "status": "pending_verification",
        "ai_check": {
            "is_valid_observation": is_valid,
            "confidence": confidence,
            "observation_type": observation_type
        },
        "auto_escalated": auto_escalated,
        "message": "Report submitted. Authorities will verify shortly."
    }

@router.get("/reports")
def get_all_reports(db: Session = Depends(get_db)):
    reports = db.query(CommunityReport)\
                .order_by(CommunityReport.submitted_at.desc())\
                .all()
    return [
        {
            "id": f"RPT_{r.id:04d}",
            "latitude": r.latitude,
            "longitude": r.longitude,
            "observation_type": r.observation_type,
            "description": r.description,
            "ai_verified": r.ai_verified,
            "status": r.status,
            "submitted_at": r.submitted_at
        }
        for r in reports
    ]

@router.post("/verify/{report_id}")
def verify_report(
    report_id: int,
    action: str = Form(...),
    db: Session = Depends(get_db)
):
    report = db.query(CommunityReport)\
               .filter(CommunityReport.id == report_id)\
               .first()

    if not report:
        return {"error": "Report not found"}

    report.status = "verified" if action == "approve" else "rejected"
    db.commit()

    return {
        "report_id": f"RPT_{report_id:04d}",
        "new_status": report.status
    }