from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
import bcrypt

from models import User
from db.database import get_db
from utils.utils import create_access_token, decode_token

router = APIRouter()


# ------------------ SCHEMAS ------------------

class SignUp(BaseModel):
    username: str
    password: str
    email: str


class Login(BaseModel):
    username: str
    password: str


# ------------------ SIGNUP ------------------

@router.post("/signup")
def signup(userData: SignUp, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        or_(
            User.username == userData.username,
            User.email == userData.email
        )
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = bcrypt.hashpw(userData.password.encode(), bcrypt.gensalt())

    new_user = User(
        username=userData.username,
        password=hashed_pw.decode(),
        email=userData.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access = create_access_token({"sub": new_user.id})

    return {
        "access_token": access,
        "token_type": "bearer"
    }


# ------------------ LOGIN ------------------

@router.post("/login")
def login(userData: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == userData.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.checkpw(userData.password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")

    access = create_access_token({"sub": user.id})

    return {
        "access_token": access,
        "token_type": "bearer"
    }


# ------------------ LOGOUT ------------------

@router.post("/logout")
def logout():
    # In single JWT setup, logout is handled client-side
    # (delete token from frontend storage)
    return {"message": "Logout by deleting token on client side"}


# ------------------ DEBUG ------------------

@router.get("/debug/decode")
def debug_decode(token: str):
    return decode_token(token)
