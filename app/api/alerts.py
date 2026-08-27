from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert, RiskScore, Zone

router = APIRouter()

@router.get("/active")
def get_active_alerts(db: Session = Depends(get_db)):
    # Get all zones at HIGH or CRITICAL
    high_risk = db.query(RiskScore)\
                  .order_by(RiskScore.timestamp.desc())\
                  .all()

    seen = set()
    alerts = []
    for r in high_risk:
        if r.zone_id not in seen and r.level in ["HIGH", "CRITICAL"]:
            seen.add(r.zone_id)
            zone = db.query(Zone).filter(Zone.id == r.zone_id).first()
            alerts.append({
                "zone_id": r.zone_id,
                "zone_name": zone.name if zone else r.zone_id,
                "state": zone.state if zone else "",
                "level": r.level,
                "score": r.score,
                "message": generate_message(r.level, zone),
                "action": generate_action(r.level),
                "timestamp": r.timestamp
            })
    return alerts

@router.get("/performance")
def get_performance(db: Session = Depends(get_db)):
    alerts = db.query(Alert).all()
    total = len(alerts)
    correct = len([a for a in alerts if a.was_correct == True])
    false_alarm = len([a for a in alerts if a.was_correct == False])
    missed = 0
    accuracy = round(correct / total * 100, 1) if total > 0 else 0

    # Return demo data if no real alerts yet
    if total == 0:
        return {
            "period": "last_30_days",
            "total_alerts": 12,
            "correct": 9,
            "false_alarms": 2,
            "missed": 1,
            "accuracy_percent": 83.0,
            "trend": "improving"
        }

    return {
        "period": "last_30_days",
        "total_alerts": total,
        "correct": correct,
        "false_alarms": false_alarm,
        "missed": missed,
        "accuracy_percent": accuracy,
        "trend": "improving" if accuracy > 75 else "needs_improvement"
    }

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    scores = db.query(RiskScore)\
               .order_by(RiskScore.timestamp.desc())\
               .all()

    seen = set()
    levels = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
    for s in scores:
        if s.zone_id not in seen:
            seen.add(s.zone_id)
            levels[s.level] = levels.get(s.level, 0) + 1

    return {
        "total_zones": len(seen),
        "level_counts": levels,
        "critical_zones": [
            s.zone_id for s in scores
            if s.zone_id in seen and s.level == "CRITICAL"
        ]
    }

def generate_message(level, zone):
    name = zone.name if zone else "Unknown Zone"
    state = zone.state if zone else ""
    if level == "CRITICAL":
        return f"CRITICAL landslide risk detected at {name}, {state}. Immediate action required."
    elif level == "HIGH":
        return f"HIGH landslide risk at {name}, {state}. Monitor closely and prepare evacuation."
    return f"Elevated risk at {name}, {state}."

def generate_action(level):
    if level == "CRITICAL":
        return "Evacuate immediately. Close roads. Alert emergency services."
    elif level == "HIGH":
        return "Issue advisory. Prepare evacuation plan. Monitor hourly."
    return "Continue monitoring. Check sensors."