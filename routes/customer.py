from fastapi import APIRouter, Depends, Header, HTTPException,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.database import get_db
from models import Customer, Incident
from utils.utils import decode_token
from pydantic import BaseModel
from sqlalchemy.inspection import inspect

import requests as http_requests
router = APIRouter()

class ConversationRequest(BaseModel):
    token: str
    conversation: str

class ManualReportRequest(BaseModel):
    token: str

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


def get_customer_from_token(token: str, db: Session):
    decoded = decode_token(token)
    user_id = int(decoded["sub"])
    role = decoded["role"]
    if role == "officer":
        raise HTTPException(status_code=403, detail="Incorrect route")
    user = db.query(Customer).filter(Customer.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/analyze")
def analyze_conversation(data: ConversationRequest, db: Session = Depends(get_db)):
    user = get_customer_from_token(data.token, db)

    try:
        response = http_requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "gemma3:4b",
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Analyze the following conversation and determine if it contains signs of domestic violence or aggression.
Respond with ONLY one word: True or False.

Conversation:
{data.conversation}"""
                    }
                ],
                "stream": False
            },
            timeout=60
        )
        result = response.json()["message"]["content"].strip()
        print(f"OLLAMA RESULT: '{result}'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama server error: {str(e)}")

    if result.lower() == "true":
        incident = Incident(
            customer_id=user.id,
            description=f"Auto-detected from conversation analysis:\n{data.conversation}",
            location=user.address,
            status="initialized"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return {
            "flagged": True,
            "incident_id": incident.id,
            "message": "Incident created based on conversation analysis"
        }

    return {"flagged": False, "message": "No signs of domestic violence detected"}
@router.post("/report")
def manual_report(data: ManualReportRequest, db: Session = Depends(get_db)):
    user = get_customer_from_token(data.token, db)

    incident = Incident(
        customer_id=user.id,
        description="Manual report initiated by customer",
        location=user.address,
        status="initialized"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident reported successfully",
        "incident_id": incident.id,
        "status": incident.status,
        "created_at": incident.created_at
    }
