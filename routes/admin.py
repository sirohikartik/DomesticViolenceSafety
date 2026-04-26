from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy.inspection import inspect
from pydantic import BaseModel
from db.database import get_db
from models import Customer, Officer, Incident
from utils.utils import create_access_token, decode_token
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")

router = APIRouter()


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    token: str

class UpdateIncident(BaseModel):
    token: str
    incident_id: int
    status: str | None = None
    officer_id: int | None = None
    description: str | None = None
    location: str | None = None

class UpdateCustomerAdmin(BaseModel):
    token: str
    customer_id: int
    email: str | None = None
    phone: str | None = None
    address: str | None = None

class UpdateOfficerAdmin(BaseModel):
    token: str
    officer_id: int
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    department: str | None = None


# ─── Helper ───────────────────────────────────────────────────────────────────

def verify_admin(token: str):
    decoded = decode_token(token)
    if decoded.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return decoded

def strip_password(obj) -> dict:
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
        if c.key != "password"
    }


# ─── Auth ─────────────────────────────────────────────────────────────────────

@router.post("/login")
def admin_login(data: AdminLogin):
    if data.username != ADMIN_USERNAME or data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    token = create_access_token({"sub": "admin", "role": "admin"})
    return {"access_token": token}


# ─── Customers ────────────────────────────────────────────────────────────────

@router.post("/customers")
def get_all_customers(data: AdminToken, db: Session = Depends(get_db)):
    verify_admin(data.token)
    customers = db.query(Customer).all()
    return [strip_password(c) for c in customers]

@router.put("/customers")
def update_customer(data: UpdateCustomerAdmin, db: Session = Depends(get_db)):
    verify_admin(data.token)
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if data.email:
        customer.email = data.email
    if data.phone:
        customer.phone = data.phone
    if data.address:
        customer.address = data.address
    db.commit()
    db.refresh(customer)
    return strip_password(customer)


# ─── Officers ─────────────────────────────────────────────────────────────────

@router.post("/officers")
def get_all_officers(data: AdminToken, db: Session = Depends(get_db)):
    verify_admin(data.token)
    officers = db.query(Officer).all()
    return [strip_password(o) for o in officers]

@router.put("/officers")
def update_officer(data: UpdateOfficerAdmin, db: Session = Depends(get_db)):
    verify_admin(data.token)
    officer = db.query(Officer).filter(Officer.id == data.officer_id).first()
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
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


# ─── Incidents ────────────────────────────────────────────────────────────────

@router.post("/incidents")
def get_all_incidents(data: AdminToken, db: Session = Depends(get_db)):
    verify_admin(data.token)
    incidents = db.query(Incident).all()
    return [
        {c.key: getattr(i, c.key) for c in inspect(i).mapper.column_attrs}
        for i in incidents
    ]

@router.put("/incidents")
def update_incident(data: UpdateIncident, db: Session = Depends(get_db)):
    print(f"INCIDENT ID: {data.incident_id}")
    print(f"ALL DATA: {data}")
    incident = db.query(Incident).filter(Incident.id == data.incident_id).first()
    print(f"INCIDENT FOUND: {incident}")
    verify_admin(data.token)
    incident = db.query(Incident).filter(Incident.id == data.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if data.status:
        incident.status = data.status
    if data.officer_id is not None and data.officer_id != 0:  # guard against 0 or None
        officer = db.query(Officer).filter(Officer.id == data.officer_id).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        incident.officer_id = data.officer_id
    if data.description:
        incident.description = data.description
    if data.location:
        incident.location = data.location
    db.commit()
    db.refresh(incident)
    return {c.key: getattr(incident, c.key) for c in inspect(incident).mapper.column_attrs}
