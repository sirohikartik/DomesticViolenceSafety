from fastapi import FastAPI
from models import Base
from db.database import engine
from routes.auth import router as auth_router

app = FastAPI()

try :
    Base.metadata.drop_all(bind = engine)
    Base.metadata.create_all(bind=engine)
    print("Database initialized")
except Exception as e:
    print(f"Exception occurred while creating database {e}")

@app.get("/test")
def test():
    return {"Hello":"World"}

app.include_router(auth_router, prefix="/auth")
