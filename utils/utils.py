from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Header,HTTPException
import os
from dotenv import load_dotenv
import requests
import time

import math
load_dotenv()

geo_cache =  {}

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    print(f"TOKEN RECEIVED: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")




def geocode(address: str):
    if address in geo_cache:
        return geo_cache[address]

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json"
    }

    res = requests.get(url, params=params, headers={"User-Agent": "test-app"}).json()

    time.sleep(1)  # avoid rate limit (IMPORTANT)

    if res:
        lat, lon = float(res[0]["lat"]), float(res[0]["lon"])
        geo_cache[address] = (lat, lon)
        return lat, lon

    return None, None



def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c
