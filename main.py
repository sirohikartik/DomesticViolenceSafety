from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models import Base
from db.database import engine
from routes.auth import router as auth_router
from routes.customer import router as cust_router 
from routes.officer import router as officer_router 
from routes.admin import router as admin
import aiofiles
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")
except Exception as e:
    print(f"Error initializing database: {e}")

@app.get("/test")
def test():
    return {"Hello":"World"}


@app.get("/")
async def serve_frontend():
    async with aiofiles.open("frontend/app.html", mode="r") as f:
        html_content = await f.read()
    return HTMLResponse(content=html_content, status_code=200)

app.include_router(auth_router, prefix="/auth")
app.include_router(cust_router, prefix="/customer")
app.include_router(admin,prefix="/admin")
app.include_router(officer_router, prefix="/officer")
