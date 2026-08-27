from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Zone, RiskScore

router = APIRouter()

# Hardcoded impact data per zone (in real system this comes from OSM)
IMPACT_DATA = {
    "MEG_001": {
        "roads": [
            {"name": "NH-6", "stretch": "3.1km", "risk": "CRITICAL"},
            {"name": "State Highway 5", "stretch": "1.2km", "risk": "HIGH"}
        ],
        "villages": [
            {"name": "Sohra Village", "houses": 62, "distance_m": 180},
            {"name": "Mawsmai", "houses": 34, "distance_m": 420}
        ],
        "schools": [
            {"name": "Sohra Primary School", "distance_m": 95},
        ],
        "bridges": [
            {"name": "Mawsmai Bridge", "risk": "HIGH"}
        ],
        "hospitals": []
    },
    "SIK_001": {
        "roads": [
            {"name": "NH-10", "stretch": "2.3km", "risk": "HIGH"}
        ],
        "villages": [
            {"name": "Lingtam", "houses": 45, "distance_m": 200},
        ],
        "schools": [
            {"name": "Lingtam Primary School", "distance_m": 120}
        ],
        "bridges": [
            {"name": "Rongli Bridge", "risk": "MEDIUM"}
        ],
        "hospitals": [
            {"name": "Rongli PHC", "distance_m": 650}
        ]
    },
    "MAN_001": {
        "roads": [
            {"name": "NH-37", "stretch": "1.8km", "risk": "MODERATE"}
        ],
        "villages": [
            {"name": "Porompat", "houses": 28, "distance_m": 310}
        ],
        "schools": [],
        "bridges": [],
        "hospitals": [
            {"name": "RIMS Hospital", "distance_m": 1200}
        ]
    },
    "ARU_001": {
        "roads": [
            {"name": "NH-415", "stretch": "2.7km", "risk": "HIGH"},
        ],
        "villages": [
            {"name": "Naharlagun East", "houses": 89, "distance_m": 150}
        ],
        "schools": [
            {"name": "Govt Higher Secondary", "distance_m": 230}
        ],
        "bridges": [
            {"name": "Dikrong Bridge", "risk": "HIGH"}
        ],
        "hospitals": []
    },
    "MIZ_001": {
        "roads": [
            {"name": "NH-54", "stretch": "4.2km", "risk": "CRITICAL"},
            {"name": "Aizawl Ring Road", "stretch": "0.9km", "risk": "HIGH"}
        ],
        "villages": [
            {"name": "Zemabawk", "houses": 112, "distance_m": 90},
            {"name": "Durtlang", "houses": 78, "distance_m": 260}
        ],
        "schools": [
            {"name": "Zemabawk HS School", "distance_m": 145},
            {"name": "Durtlang Primary", "distance_m": 310}
        ],
        "bridges": [
            {"name": "Tlawng Bridge", "risk": "CRITICAL"}
        ],
        "hospitals": [
            {"name": "Civil Hospital Aizawl", "distance_m": 890}
        ]
    }
}

@router.get("/{zone_id}")
def get_impact(zone_id: str, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        return {"error": "Zone not found"}

    latest_risk = db.query(RiskScore)\
                    .filter(RiskScore.zone_id == zone_id)\
                    .order_by(RiskScore.timestamp.desc())\
                    .first()

    impact = IMPACT_DATA.get(zone_id, {
        "roads": [], "villages": [],
        "schools": [], "bridges": [], "hospitals": []
    })

    total_people = sum(v["houses"] * 4 for v in impact.get("villages", []))

    return {
        "zone_id": zone_id,
        "zone_name": zone.name,
        "risk_level": latest_risk.level if latest_risk else "UNKNOWN",
        "estimated_people_affected": total_people,
        "impact": impact
    }