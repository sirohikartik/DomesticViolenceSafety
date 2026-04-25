from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

import os
load_dotenv(dotenv_path = ".env")

DATABASE_URL = os.getenv("DB")

if DATABASE_URL is None:
    print("ERROR : Database url not found in env")
else:
    print("Database path found")

try :
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
            print("Database connected successfully")
    SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
except Exception as e :
    print(f"Could not initiate Databse due to {e}")

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
