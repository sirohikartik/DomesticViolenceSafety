from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
import bcrypt

from models import Customer, Officer
from db.database import get_db
from utils.utils import create_access_token

router = APIRouter()



class SignUp(BaseModel):
    username: str
    password: str
    email: str
    phone : str
    address : str
    role: str = "customer"
    badge_num : str | None = None 
    dept : str | None = None


class Login(BaseModel):
    username: str
    password: str



@router.post("/signup")
def signup(userData: SignUp, db: Session = Depends(get_db)):

    if userData.role not in ["customer", "officer"]:
        raise HTTPException(status_code=400, detail="Role must be 'customer' or 'officer'")

    existing_customer = db.query(Customer).filter(
        or_(Customer.username == userData.username,
            Customer.email == userData.email,
            Customer.phone == userData.phone)
    ).first()

    existing_officer = db.query(Officer).filter(
        or_(Officer.username == userData.username,
            Officer.email == userData.email,
            Officer.phone == userData.phone
            )
    ).first()

    if existing_customer or existing_officer:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = bcrypt.hashpw(userData.password.encode(), bcrypt.gensalt()).decode()

    if userData.role == "customer":
        new_user = Customer(
            username=userData.username,
            password=hashed_pw,
            email=userData.email,
            phone = userData.phone,
            address = userData.address
        )

    else:
        new_user = Officer(
            username=userData.username,
            password=hashed_pw,
            email=userData.email,
            phone = userData.phone,
            location = userData.address,
            department = userData.dept,
            badge_number = userData.badge_num
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({
        "sub": str(new_user.id),
        "role": userData.role
    })

    return {"access_token": token}



@router.post("/login")
def login(userData: Login, db: Session = Depends(get_db)):

    user = db.query(Customer).filter(Customer.username == userData.username).first()
    role = "customer"

    if not user:
        user = db.query(Officer).filter(Officer.username == userData.username).first()
        role = "officer"

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.checkpw(userData.password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "sub": str(user.id),
        "role": role
    })

    return {"access_token": token}
