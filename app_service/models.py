from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from datetime import datetime
from database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    specialization = Column(String)
    available_slots = Column(JSON, nullable=True)
    daily_limit = Column(Integer, default=10)
    booked_slots = Column(Integer, default=10)

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer,primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)

