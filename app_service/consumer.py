import json
import pika
import os
import time
import logging
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Doctor, Base, Patient

# ---------------------------------------------------------------------
# 🧩 LOGGING CONFIGURATION
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("consumer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# 🧩 DATABASE INITIALIZATION
# ---------------------------------------------------------------------
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Worker database initialized and tables verified")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}")

# ---------------------------------------------------------------------
# 🧩 FUNCTION TO HANDLE EVENTS
# ---------------------------------------------------------------------
def handle_user_created(event_data):
    """
    Handles user.created events.
    Creates corresponding Doctor or Patient records in the healthcare DB.
    """
    user_id = event_data.get("user_id")
    role = event_data.get("role")
    email = event_data.get("email")
    profile = event_data.get("profile", {})

    db: Session = SessionLocal()
    try:
        if role == "doctor":
            name = profile.get("name", email.split("@")[0].capitalize())
            specialization = profile.get("specialization", "General")

            logger.info(f"👨‍⚕️ Creating doctor record for user_id={user_id}, name={name}, specialization={specialization}")

            existing = db.query(Doctor).filter(Doctor.user_id == user_id).first()
            if existing:
                logger.warning(f"⚠️ Doctor already exists for user_id={user_id}")
                return

            new_doctor = Doctor(
                user_id=user_id,
                name=name,
                specialization=specialization,
                available_slots=["09:00", "09:30", "10:00", "10:30", "11:00"],
                daily_limit=5,
                booked_slots=0
            )
            db.add(new_doctor)
            db.commit()
            logger.info(f"✅ Doctor record created successfully for user_id={user_id}")

        elif role == "patient":
            name = profile.get("name", email.split("@")[0].capitalize())
            phone = profile.get("phone", "N/A")

            logger.info(f"🧍 Creating patient record for user_id={user_id}, name={name}, phone={phone}")

            existing = db.query(Patient).filter(Patient.user_id == user_id).first()
            if existing:
                logger.warning(f"⚠️ Patient already exists for user_id={user_id}")
                return

            new_patient = Patient(
                user_id=user_id,
                name=name,
                email=email,
                phone=phone
            )
            db.add(new_patient)
            db.commit()
            logger.info(f"✅ Patient record created successfully for user_id={user_id}")

        else:
            logger.info(f"Skipping user_id={user_id} — role '{role}' is not handled.")
            return

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to process user.created for user_id={user_id}: {e}")

    finally:
        db.close()

def handle_appointment_created(event_data):
    """Handles appointment.created events."""
    doctor_id = event_data.get("doctor_id")
    patient_id = event_data.get("patient_id")
    time = event_data.get("time")

    db: Session = SessionLocal()
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        patient = db.query(Patient).filter(Patient.id == patient_id).first()

        if not doctor or not patient:
            logger.warning(f"⚠️ Doctor or patient not found (doctor_id={doctor_id}, patient_id={patient_id})")
            return

        logger.info(f"📅 Appointment confirmed | Doctor={doctor.name}, Patient={patient.name}, Time={time}")

        # Example future action: trigger notification or analytics
        # send_email(patient.email, f"Your appointment with Dr. {doctor.name} at {time} is confirmed")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to process appointment.created event: {e}")
    finally:
        db.close()

# ---------------------------------------------------------------------
# 🧩 CALLBACK FUNCTION (RabbitMQ Consumer)
# ---------------------------------------------------------------------
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        event = data.get("event")
        logger.info(f"📥 Received event '{event}': {data}")

        if event == "user.created":
            handle_user_created(data)
        elif event == "appointment.created":
            handle_appointment_created(data)
        else:
            logger.warning(f"⚠️ Unknown event type received: {event}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# ---------------------------------------------------------------------
# 🧩 RABBITMQ CONNECTION (with retry)
# ---------------------------------------------------------------------
def connect_to_rabbitmq(max_retries=10, delay=5):
    """Retry connection to RabbitMQ until available."""
    rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🐇 Attempting to connect to RabbitMQ (try {attempt}/{max_retries})...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
            logger.info("✅ Connected to RabbitMQ successfully")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"❌ RabbitMQ not ready yet: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    logger.error(f"🚨 Could not connect to RabbitMQ after {max_retries} attempts. Exiting.")
    exit(1)

# ---------------------------------------------------------------------
# 🧩 MAIN CONSUMER LOGIC
# ---------------------------------------------------------------------
def main():
    try:
        connection = connect_to_rabbitmq()
        channel = connection.channel()
        channel.exchange_declare(exchange="users", exchange_type="topic", durable=True)

        # Declare queue for worker
        channel.queue_declare(queue="user_created_queue", durable=True)
        channel.queue_bind(exchange="users", queue="user_created_queue", routing_key="user.created")

        logger.info("🚀 Worker listening on exchange 'users' for event 'user.created'...")
        channel.basic_consume(queue="user_created_queue", on_message_callback=callback)

        channel.start_consuming()
    except Exception as e:
        logger.error(f"❌ Worker failed to start: {e}")

# ---------------------------------------------------------------------
# 🧩 ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()
