import os
from dotenv import load_dotenv

# Load once, from project root
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
ALGO = os.getenv("ALGORITHM", "HS256")
ACCESS_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET_KEY not set")

if ALGO != "HS256":
    # keep it simple for now
    raise RuntimeError(f"Unexpected ALGORITHM={ALGO}")
