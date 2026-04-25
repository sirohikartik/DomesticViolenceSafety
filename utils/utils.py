from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException
from settings import JWT_SECRET, ALGO, ACCESS_EXPIRE_MIN, REFRESH_EXPIRE_DAYS



def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({
        "sub": str(data["sub"]),   # 🔥 force string
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MIN),
        "type": "access"
    })
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGO)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    to_encode.update({
        "sub": str(data["sub"]),   # 🔥 force string
        "exp": datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS),
        "type": "refresh"
    })
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGO)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGO])
        return payload
    except JWTError as e:
        # print once so you actually see the real cause
        print("JWT ERROR:", repr(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")
