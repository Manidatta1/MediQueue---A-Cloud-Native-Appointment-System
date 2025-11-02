from database import SessionLocal
from models import  Doctor, Patient, Appointment
from sqlalchemy.exc import IntegrityError
from datetime import datetime

db = SessionLocal()

try:
    # 🧹 Clear all existing data
    db.query(Appointment).delete()
    db.query(Doctor).delete()
    db.query(Patient).delete()
    db.commit()

    # 🩺 2️⃣ Seed Doctors (linked via user_id)
    doctors = [
        Doctor(
            user_id=1,
            name="Dr. Alice Johnson",
            specialization="Cardiology",
            daily_limit=5,
            booked_slots=0,
            available_slots=["09:00", "09:30", "10:00", "10:30", "11:00"]
        ),
        Doctor(
            user_id=2,
            name="Dr. Bob Smith",
            specialization="Neurology",
            daily_limit=4,
            booked_slots=0,
            available_slots=["10:00", "10:30", "11:00", "11:30"]
        ),
        Doctor(
            user_id=3,
            name="Dr. Clara Williams",
            specialization="Dermatology",
            daily_limit=3,
            booked_slots=0,
            available_slots=["13:00", "13:30", "14:00"]
        ),
    ]

    db.add_all(doctors)
    db.commit()
    print("✅ Doctors table seeded")

    # 👥 3️⃣ Seed Patients (linked via user_id)
    patients = [
        Patient(user_id=4, name="John Doe", email="john@example.com", phone="555-1010"),
        Patient(user_id=5, name="Jane Smith", email="jane@example.com", phone="555-2020"),
        Patient(user_id=6, name="Liam Johnson", email="liam@example.com", phone="555-4040"),
    ]

    db.add_all(patients)
    db.commit()
    print("✅ Patients table seeded")

    print("\n🎉 All data seeded successfully!")

except IntegrityError as e:
    db.rollback()
    print(f"⚠️ IntegrityError: {e}")

finally:
    db.close()
