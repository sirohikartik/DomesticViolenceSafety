from fastapi import FastAPI
from models import Base
from db.database import engine
from routes.auth import router as auth_router
from routes.customer import router as cust_router 
#from routes.officer import router as officer_router 
app = FastAPI()

try:
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")
except Exception as e:
    print(f"Error initializing database: {e}")

@app.get("/test")
def test():
    return {"Hello":"World"}

app.include_router(auth_router, prefix="/auth")
app.include_router(cust_router, prefix="/customer")

#app.include_router(officer_router, prefix="/officer")
