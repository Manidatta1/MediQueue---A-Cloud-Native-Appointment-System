import os
import json
import logging
from datetime import datetime, date
import requests
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import distinct
import redis
import pika
from typing import List
from jose import jwt, JWTError
from auth_utils import verify_token_remote 
from pydantic import BaseModel

from database import SessionLocal, engine
from models import Base, Doctor, Patient, Appointment

from fastapi.middleware.cors import CORSMiddleware

REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "http://auth-service:8001")

# ---------------------------------------------------------------------
# 🧩 CONFIGURATION
# ---------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "xyz")
ALGORITHM = "HS256"

# ---------------------------------------------------------------------
# 🧩 LOGGING CONFIGURATION
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # logs to file
        logging.StreamHandler()          # logs to console
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Healthcare Appointment Service",root_path="/api")

origins = [
    "http://localhost:5173",  # Vite dev
    "http://127.0.0.1:5173",
    "http://frontend_service:5173",  # Docker internal
    "*"  # optional during dev
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------
# 🧩 HELPER — Verify and Decode JWT
# ---------------------------------------------------------------------
def get_current_user(Authorization: str = Header(None)):
    if not Authorization or not Authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = Authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # contains { "sub": "user_id", "role": "doctor" }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---------------------------------------------------------------------
# 🧩 DATABASE INITIALIZATION
# ---------------------------------------------------------------------
Base.metadata.create_all(bind=engine)
logger.info("✅ Database tables created successfully")

# ---------------------------------------------------------------------
# 🧩 REDIS SETUP
# ---------------------------------------------------------------------
try:
    redis_host = os.getenv("REDIS_HOST", "redis")
    r = redis.Redis(host=redis_host, port=6379, decode_responses=True) 
    r.ping()
    logger.info("✅ Connected to Redis successfully")
except Exception as e:
    logger.error(f"❌ Redis connection failed: {e}")

# ---------------------------------------------------------------------
# 🧩 HELPER FUNCTIONS
# ---------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_rabbit_connection():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "rabbitmq"))
        )
        channel = connection.channel()
        channel.exchange_declare(exchange="appointments", exchange_type="topic", durable=True)
        logger.info("✅ Connected to RabbitMQ and exchange declared")
        return connection, channel
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ")


# ---------------------------------------------------------------------
# 🧩 ROUTES
# ---------------------------------------------------------------------

@app.get("/")
def home():
    logger.info("🌐 Home endpoint called")
    return {"message": "Healthcare Appointment API is running"}



@app.get("/doctors")
def get_all_doctors(db: Session = Depends(get_db)):
    logger.info("📥 GET /doctors called")
    doctors = db.query(Doctor).all()
    logger.info(f"Fetched {len(doctors)} doctors from database")
    return [
        {
            "id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "available_slots": d.available_slots,
            "booked_slots": d.booked_slots,
            "daily_limit": d.daily_limit
        }
        for d in doctors
    ]


@app.get("/doctor/specializations")
def get_specializations(db: Session = Depends(get_db)):
    logger.info("📥 GET /doctor/specializations called")
    specializations = db.query(distinct(Doctor.specialization)).all()
    logger.info(f"Fetched {len(specializations)} specializations from database")
    return [s[0] for s in specializations if s[0]]


@app.get("/doctor/search")
def search_doctor(specialization: str = None, name: str = None, db: Session = Depends(get_db)):
    query = db.query(Doctor)
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    if name:
        query = query.filter(Doctor.name.ilike(f"%{name}%"))
    doctors = query.all()

    if not doctors:
        raise HTTPException(status_code=404, detail="No matching doctors found")

    return [
        {
            "id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "available_slots": d.available_slots or [],
            "booked_slots": d.booked_slots,
            "daily_limit": d.daily_limit
        }
        for d in doctors
    ]



@app.post("/register_patient")
def register_patient(
    name: str,
    email: str,
    phone: str,
    Authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    logger.info(f"🧾 Register patient endpoint called | name={name}, email={email}")
    logger.info(f"🪪 Raw Authorization header received: {Authorization}")

    # ✅ Verify JWT
    try:
        payload = verify_token_remote(Authorization)
        user_id = payload.get("sub")
        role = payload.get("role")
        logger.info(f"🔑 Token verified for user_id={user_id}, role={role}")
    except Exception as e:
        logger.error(f"❌ Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # ✅ Role check
    if role != "patient":
        logger.warning(f"🚫 Unauthorized access attempt by role={role}")
        raise HTTPException(status_code=403, detail="Only patients can register")

    # ✅ Proceed with registration
    existing = db.query(Patient).filter(Patient.email == email).first()
    if existing:
        logger.warning(f"⚠️ Email already registered: {email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    new_patient = Patient(name=name, email=email, phone=phone, user_id=user_id)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    logger.info(f"✅ Patient registered successfully | patient_id={new_patient.id} user_id={user_id}")
    return {"message": "Patient registered successfully!", "patient_id": new_patient.id}


@app.post("/book")
def book(
    doctor_id: int,
    time: str,
    Authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    formatted_time = time
    logger.info(f"🩺 Booking request | doctor_id={doctor_id}, time={formatted_time}")
    logger.info(f"🪪 Raw Authorization header received: {Authorization}")

    # ✅ Verify JWT
    try:
        payload = verify_token_remote(Authorization)
        user_id = payload.get("sub")
        role = payload.get("role")
        logger.info(f"🔑 Token verified for user_id={user_id}, role={role}")
    except Exception as e:
        logger.error(f"❌ Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if role != "patient":
        logger.warning(f"🚫 Unauthorized booking attempt by role={role}")
        raise HTTPException(status_code=403, detail="Only patients can book appointments")

    # ✅ Find patient by user_id
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        logger.warning(f"⚠️ Patient not found in DB for user_id={user_id}")
        raise HTTPException(status_code=404, detail="Patient record not found")
  
    key = f"lock:doctor:{doctor_id}:{formatted_time}"
    if not r.set(key, "locked", nx=True, ex=60):
        logger.warning(f"⚠️ Lock acquisition failed for {key} — another booking in progress")
        raise HTTPException(status_code=400, detail="Slot already being booked. Try another time.")
    logger.info(f"✅ Redis lock acquired for {key}")

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # ✅ Check slot availability
    available_slots = doctor.available_slots or []
    if formatted_time not in available_slots:
        logger.warning(f"❌ Slot {formatted_time} not available for doctor {doctor_id}")
        raise HTTPException(status_code=400, detail=f"Slot {formatted_time} not available")

    # ✅ Create appointment
    full_time = datetime.combine(date.today(), datetime.strptime(time, "%H:%M").time())
    new_appointment = Appointment(doctor_id=doctor_id, patient_id=patient.id, time=full_time)
    db.add(new_appointment)

    updated_slots = [slot for slot in doctor.available_slots if slot != formatted_time]
    doctor.available_slots = updated_slots
    doctor.booked_slots += 1
    db.commit()
    db.refresh(new_appointment)
    logger.info(f"✅ Appointment created successfully | appointment_id={new_appointment.id}")

    # 📨 Publish to RabbitMQ
    try:
        connection, channel = get_rabbit_connection()
        message = {
            "appointment_id": new_appointment.id,
            "doctor_id": doctor_id,
            "patient_id": patient.id,
            "time": formatted_time
        }
        channel.basic_publish(
            exchange="appointments",
            routing_key="appointment.created",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info(f"📤 Message published to RabbitMQ: {message}")
        connection.close()
    except Exception as e:
        logger.error(f"❌ RabbitMQ publish failed: {e}")
        return {"status": "Booked, but RabbitMQ publish failed", "error": str(e)}

    return {"message": "Appointment booked successfully", "appointment_id": new_appointment.id}


@app.get("/patient")
def get_patient(
    Authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Fetch logged-in patient’s details by token.
    """
    logger.info("📥 GET /patient called")
    logger.info(f"🪪 Raw Authorization header received: {Authorization}")

    try:
        payload = verify_token_remote(Authorization)
        user_id = payload.get("sub")
        role = payload.get("role")
        logger.info(f"🔑 Token verified for user_id={user_id}, role={role}")
    except Exception as e:
        logger.error(f"❌ Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if role != "patient":
        logger.warning(f"🚫 Unauthorized role access: {role}")
        raise HTTPException(status_code=403, detail="Only patients can access this endpoint")

    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    logger.info(f"✅ Returning patient info for user_id={user_id}")
    return {
        "patient_id": patient.id,
        "name": patient.name,
        "email": patient.email,
        "phone": patient.phone
    }

# ---------------------------------------------------------------------
# 🧩 ROUTE — Update Doctor Availability
# ---------------------------------------------------------------------

class SlotsUpdateRequest(BaseModel):
    available_slots: List[str]

@app.put("/doctor/slots/update")
def update_doctor_slots(
    slots: SlotsUpdateRequest,
    Authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    logger.info("🧾 Received request to update doctor slots.")
    logger.info(f"🪪 Raw Authorization header received: {Authorization}")
    logger.info(f"🪪  requested slots: {slots}")

    # ✅ Verify JWT
    try:
        payload = verify_token_remote(Authorization)
        user_id = payload.get("sub")
        role = payload.get("role")
        logger.info(f"🔑 Token verified for user_id={user_id}, role={role}")
    except Exception as e:
        logger.error(f"❌ Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # ✅ Check role
    if role != "doctor":
        logger.warning(f"🚫 Unauthorized role access: user_id={user_id}, role={role}")
        raise HTTPException(status_code=403, detail="Only doctors can update slots")

    # ✅ Fetch doctor record
    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if not doctor:
        logger.warning(f"⚠️ Doctor not found in DB for user_id={user_id}")
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    available_slots = slots.available_slots

    # ✅ Update slots
    old_slots = doctor.available_slots
    doctor.available_slots = available_slots
    db.commit()
    db.refresh(doctor)

    logger.info(
        f"✅ Doctor slots updated successfully for user_id={user_id} | "
        f"Old slots: {old_slots} → New slots: {doctor.available_slots}"
    )

    return {
        "message": "Doctor slots updated successfully",
        "doctor_id": doctor.id,
        "available_slots": doctor.available_slots
    }

@app.post("/doctor/slots/reset")
def reset_doctor_slots(db: Session = Depends(get_db)):
    logger.info("🕑 Running daily slot reset task...")

    doctors = db.query(Doctor).all()
    for doc in doctors:
        doc.available_slots = ["09:00", "09:30", "10:00", "10:30", "11:00"]
        doc.booked_slots = 0
    db.commit()

    logger.info(f"✅ Reset slots for {len(doctors)} doctors at {datetime.now()}")
    return {"message": f"Reset slots for {len(doctors)} doctors"}

@app.post("/logout")
def logout(Authorization: str = Header(None)):
    if not Authorization or not Authorization.lower().startswith("bearer "):
        logger.warning("⚠️ Logout failed — missing Authorization header")
        raise HTTPException(status_code=401, detail="Missing token")

    token = Authorization.split(" ")[1]

    try:
        # Decode token to get expiry time
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiry_time = payload["exp"]
        ttl = expiry_time - int(datetime.utcnow().timestamp())

        if ttl <= 0:
            logger.warning(f"⚠️ Token already expired for user_id={payload.get('sub')}")
            raise HTTPException(status_code=400, detail="Token already expired")

        # Store token in Redis blacklist with same TTL
        r.setex(f"blacklist:{token}", ttl, "true")

        logger.info(f"🚪 User logged out | user_id={payload.get('sub')} | role={payload.get('role')} | token blacklisted for {ttl}s")
        return {"message": "Logged out successfully"}

    except ExpiredSignatureError:
        logger.warning("⚠️ Logout failed — token already expired")
        raise HTTPException(status_code=400, detail="Token already expired")

    except InvalidTokenError:
        logger.error("❌ Logout failed — invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        logger.error(f"❌ Unexpected logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")


# ---------------------------------------------------------------------
# 🧩 MAIN
# ---------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting Healthcare Appointment API service...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
