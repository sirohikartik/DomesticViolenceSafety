from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from pydantic import BaseModel
from db.database import get_db
from models import Officer, Incident
from utils.utils import decode_token
from utils.utils import distance_km,geocode
router = APIRouter()
geo_cache = {}

# ─── Pydantic Models ──────────────────────────────────────────────────────────

class OfficerRequest(BaseModel):
    token: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    department: str | None = None

class TokenOnly(BaseModel):
    token: str

class AcceptIncidentRequest(BaseModel):
    token: str
    incident_id: int

class NearbyRequest(BaseModel):
    token: str
    radius_km: float = 5

# ─── Helper ───────────────────────────────────────────────────────────────────

def get_officer_from_token(token: str, db: Session) -> Officer:
    decoded = decode_token(token)
    user_id = int(decoded["sub"])
    role = decoded["role"]
    if role != "officer":
        raise HTTPException(status_code=403, detail="Incorrect route")
    officer = db.query(Officer).filter(Officer.id == user_id).first()
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
    return officer


def strip_password(obj) -> dict:
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
        if c.key != "password"
    }


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/me")
def get_officer_details(data: TokenOnly, db: Session = Depends(get_db)):
    officer = get_officer_from_token(data.token, db)
    return strip_password(officer)


@router.put("/me")
def update_officer_details(data: OfficerRequest, db: Session = Depends(get_db)):
    officer = get_officer_from_token(data.token, db)
    if data.email:
        officer.email = data.email
    if data.phone:
        officer.phone = data.phone
    if data.location:
        officer.location = data.location
    if data.department:
        officer.department = data.department
    db.commit()
    db.refresh(officer)
    return strip_password(officer)


@router.post("/incidents")
def get_my_incidents(data: TokenOnly, db: Session = Depends(get_db)):
    """Get all incidents assigned to this officer"""
    officer = get_officer_from_token(data.token, db)
    incidents = db.query(Incident).filter(Incident.officer_id == officer.id).all()
    return [
        {c.key: getattr(i, c.key) for c in inspect(i).mapper.column_attrs}
        for i in incidents
    ]


@router.post("/incidents/all")
def get_all_incidents(data: TokenOnly, db: Session = Depends(get_db)):
    """Get all unassigned incidents (available to pick up)"""
    get_officer_from_token(data.token, db)
    incidents = db.query(Incident).filter(Incident.officer_id == None).all()
    return [
        {c.key: getattr(i, c.key) for c in inspect(i).mapper.column_attrs}
        for i in incidents
    ]


@router.post("/incidents/accept")
def accept_incident(data: AcceptIncidentRequest, db: Session = Depends(get_db)):
    """Assign an incident to this officer"""
    officer = get_officer_from_token(data.token, db)
    incident = db.query(Incident).filter(Incident.id == data.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.officer_id is not None:
        raise HTTPException(status_code=400, detail="Incident already assigned to another officer")
    incident.officer_id = officer.id
    incident.status = "assigned"
    db.commit()
    db.refresh(incident)
    return {
        "message": "Incident accepted successfully",
        "incident_id": incident.id,
        "status": incident.status
    }


@router.post("/incidents/nearby")
def get_nearby_incidents(data: NearbyRequest, db: Session = Depends(get_db)):
    officer = get_officer_from_token(data.token, db)

    if not officer.location:
        raise HTTPException(status_code=400, detail="Officer location not set")

    off_lat, off_lon = geocode(officer.location)

    if off_lat is None:
        raise HTTPException(status_code=400, detail="Invalid officer address")

    incidents = db.query(Incident).filter(Incident.officer_id == None).all()

    nearby = []

    for i in incidents:
        if not i.location:
            continue

        lat, lon = geocode(i.location)

        if lat is None:
            continue

        dist = distance_km(off_lat, off_lon, lat, lon)

        if dist <= data.radius_km:
            nearby.append({
                "id": i.id,
                "distance_km": round(dist, 2),
                **{c.key: getattr(i, c.key) for c in inspect(i).mapper.column_attrs}
            })

    return sorted(nearby, key=lambda x: x["distance_km"])
