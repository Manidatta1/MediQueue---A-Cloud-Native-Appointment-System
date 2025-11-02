from database import SessionLocal
from models import User
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from auth_utils import hash_password

db = SessionLocal()

try:
    # 🧹 Clear all existing data
    db.query(User).delete()
    db.commit()

    # 🧑‍⚕️ 1️⃣ Seed Users (auth + roles)
    users = [
        # Doctors
        User(email="alice@hospital.com", hashed_password=hash_password("alice123"), role="doctor"),
        User(email="bob@hospital.com", hashed_password=hash_password("bob123"), role="doctor"),
        User(email="clara@hospital.com", hashed_password=hash_password("clara123"), role="doctor"),

        # Patients
        User(email="john@example.com", hashed_password=hash_password("john123"), role="patient"),
        User(email="jane@example.com", hashed_password=hash_password("jane123"), role="patient"),
        User(email="liam@example.com", hashed_password=hash_password("liam123"), role="patient"),
    ]

    db.add_all(users)
    db.commit()

    print("✅ Users table seeded")

    print("\n🎉 All data seeded successfully!")

except IntegrityError as e:
    db.rollback()
    print(f"⚠️ IntegrityError: {e}")

finally:
    db.close()
