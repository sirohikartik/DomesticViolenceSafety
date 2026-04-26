from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
import os

load_dotenv(".env")

DATABASE_URL = os.getenv("DB")

if not DATABASE_URL:
    raise Exception("❌ Database URL not found in .env")
else:
    print("✅ Database path found")

# ------------------ ENGINE ------------------

engine = create_engine(DATABASE_URL)

# ------------------ SESSION ------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ------------------ BASE (🔥 REQUIRED) ------------------

Base = declarative_base()

# ------------------ DEPENDENCY ------------------

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
