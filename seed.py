from sqlalchemy.orm import Session
from db.database import SessionLocal
from models import Officer, Customer, Incident
from datetime import datetime
import random

db: Session = SessionLocal()

# ─── SAMPLE DATA ─────────────────────────────────────────────

officer_locations = [
    "Connaught Place, Delhi",
    "Sector 17, Chandigarh",
    "Bandra, Mumbai",
    "Indiranagar, Bangalore"
]

customer_locations = [
    "Karol Bagh, Delhi",
    "Rohini, Delhi",
    "Noida Sector 62",
    "Gurgaon Cyber City",
    "Andheri East, Mumbai",
    "Powai, Mumbai",
    "Whitefield, Bangalore",
    "Salt Lake, Kolkata"
]

descriptions = [
    "Theft reported",
    "Suspicious activity",
    "Accident case",
    "Cyber fraud",
    "Missing person",
    "Robbery in progress"
]

# ─── CLEAR OLD DATA ─────────────────────────────────────────

db.query(Incident).delete()
db.query(Officer).delete()
db.query(Customer).delete()
db.commit()

# ─── CREATE OFFICERS ───────────────────────────────────────

officers = []

for i, loc in enumerate(officer_locations):
    officer = Officer(
        username=f"officer{i}",
        password="pass123",
        email=f"officer{i}@test.com",
        badge_number=f"BDG{1000 + i}",
        phone=f"99999{1000 + i}",
        location=loc,
        department="General"
    )
    db.add(officer)
    officers.append(officer)

try:
    db.commit()
except Exception as e:
    db.rollback()
    print("❌ Officer insert failed:", e)
    exit(1)

for o in officers:
    db.refresh(o)

# ─── CREATE CUSTOMERS ──────────────────────────────────────

customers = []

for i, loc in enumerate(customer_locations):
    customer = Customer(
        username=f"customer{i}",
        password="pass123",
        email=f"customer{i}@test.com",
        phone=f"98{10000000 + i}",   # REQUIRED
        address=loc                 # REQUIRED
    )
    db.add(customer)
    customers.append(customer)

try:
    db.commit()
except Exception as e:
    db.rollback()
    print("❌ Customer insert failed:", e)
    exit(1)

for c in customers:
    db.refresh(c)

print(f"Customers created: {len(customers)}")

# ─── CREATE INCIDENTS ──────────────────────────────────────

incidents = []

for i in range(20):
    loc = random.choice(customer_locations)
    desc = random.choice(descriptions)
    cust = random.choice(customers)

    incident = Incident(
        customer_id=cust.id,
        description=desc,
        location=loc,
        status="initialized",
        created_at=datetime.utcnow()
    )

    db.add(incident)
    incidents.append(incident)

try:
    db.commit()
except Exception as e:
    db.rollback()
    print("❌ Incident insert failed:", e)
    exit(1)

# ─── DONE ─────────────────────────────────────────────────

print("✅ Database seeded successfully!")
print(f"   Officers: {len(officers)}")
print(f"   Customers: {len(customers)}")
print(f"   Incidents: {len(incidents)}")
