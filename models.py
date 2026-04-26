from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    phone = Column(String, nullable=False,unique=True)
    address = Column(String, nullable=False)



class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    badge_number = Column(String, nullable=False,unique = True)
    department = Column(String, nullable=False)
    phone = Column(String, nullable = False, unique= True)

    location = Column(String, nullable=False)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customers.id"))
    officer_id = Column(Integer, ForeignKey("officers.id"), nullable=True)

    description = Column(Text)
    location = Column(String)

    status = Column(String, default="initialized")
    created_at = Column(DateTime, default=datetime.utcnow)

