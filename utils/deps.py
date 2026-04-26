from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from utils.utils import decode_token
from models import Customer


def get_current_customer(
    token: dict = Depends(decode_token),
    db: Session = Depends(get_db)
):
    try:
        user_id = int(token.get("sub"))       
    except:
        raise HTTPException(status_code=401, detail="Invalid token payload")


    role = token.get("role")

    if role != "customer":
        raise HTTPException(status_code=403, detail="Not a customer")

    user = db.query(Customer).filter(Customer.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
