from fastapi import APIRouter, Depends, Header, HTTPException,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.database import get_db
from models import Customer, Incident
from utils.utils import decode_token
from pydantic import BaseModel
from sqlalchemy.inspection import inspect
router = APIRouter()

class CustomerRequest(BaseModel):
    token: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None

@router.post("/me")
def get_details(data: CustomerRequest, db: Session = Depends(get_db)):
    decoded = decode_token(data.token)
    user_id = int(decoded["sub"])
    role = decoded["role"]
    if role == "officer":
        raise HTTPException(status_code=403, detail="Incorrect route")
    user = db.query(Customer).filter(Customer.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = {c.key: getattr(user, c.key) for c in inspect(user).mapper.column_attrs if c.key != "password"}
    return data

@router.put("/me")
def update_details(data: CustomerRequest, db: Session = Depends(get_db)):
    decoded = decode_token(data.token)
    user_id = int(decoded["sub"])
    role = decoded["role"]
    if role == "officer":
        raise HTTPException(status_code=403, detail="Incorrect route")
    user = db.query(Customer).filter(Customer.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.email:
        user.email = data.email
    if data.phone:
        user.phone = data.phone
    if data.address:
        user.address = data.address
    db.commit()
    db.refresh(user)
    data = {c.key: getattr(user, c.key) for c in inspect(user).mapper.column_attrs if c.key != "password"}
    return data
