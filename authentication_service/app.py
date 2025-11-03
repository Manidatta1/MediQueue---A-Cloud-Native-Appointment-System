from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User
from schemas import UserCreate, Token, UserLogin
from auth_utils import hash_password, verify_password, create_access_token, verify_token
from datetime import timedelta
import pika, json, os
from pika import BasicProperties
from datetime import datetime
import logging
import redis

from fastapi.middleware.cors import CORSMiddleware

REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")
SECRET_KEY = os.getenv("SECRET_KEY", "xyz")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Redis connection
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

app = FastAPI(title="Healthcare Authentication Service",root_path="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create tables
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------
# 🧩 LOGGING CONFIGURATION
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("auth_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.get("/")
def home():
    return {"message": "Auth service is running"}


def publish_user_created_event(user, profile):
    """Publishes a 'user.created' event to the RabbitMQ exchange."""
    try:
        rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
        channel = connection.channel()
        channel.exchange_declare(exchange="users", exchange_type="topic", durable=True)

        event = {
            "event": "user.created",
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "profile": profile,
            "timestamp": datetime.utcnow().isoformat()
        }

        channel.basic_publish(
            exchange="users",
            routing_key="user.created",
            body=json.dumps(event),
            properties=BasicProperties(delivery_mode=2),
        )
        logger.info(f"📤 Published event to RabbitMQ: {event}")
        connection.close()
    except Exception as e:
        logger.error(f"❌ Failed to publish user.created event: {e}")


# ---------------------------------------------------------------------
# 🧩 REGISTER ENDPOINT
# ---------------------------------------------------------------------
@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"🧾 Registration request received for {user.email} (role={user.role})")

    # Check for existing user
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        logger.warning(f"⚠️ Registration failed — Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and store user
    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"✅ User created successfully in DB with ID {new_user.id}")

    # Prepare profile data (optional)
    profile_data = user.profile or {}
    logger.info(f"📦 Profile data received for registration: {profile_data}")

    # Publish event for downstream services (e.g., app_service)
    publish_user_created_event(new_user, profile_data)

    # Create access token
    token = create_access_token({"sub": str(new_user.id), "role": new_user.role})
    logger.info(f"🔐 JWT token issued for user_id={new_user.id} role={new_user.role}")

    return {"access_token": token, "token_type": "bearer"}


# ---------------------------------------------------------------------
# 🧩 LOGIN ENDPOINT (with Logging)
# ---------------------------------------------------------------------
@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"🔐 Login attempt for {user.email}")

    db_user = db.query(User).filter(User.email == user.email).first()

    # Invalid email
    if not db_user:
        logger.warning(f"❌ Login failed — Email not found: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Invalid password
    if not verify_password(user.password, db_user.hashed_password):
        logger.warning(f"❌ Login failed — Incorrect password for {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT
    token_data = {"sub": str(db_user.id), "role": db_user.role}
    token = create_access_token(token_data)
    logger.info(f"✅ Login successful | user_id={db_user.id}, role={db_user.role}")

    return {"access_token": token, "token_type": "bearer"}


# Verify token (used by Appointment service)
@app.get("/verify-token")
def verify_token_endpoint(Authorization: str = Header(None)):
    if not Authorization or not Authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = Authorization.split(" ")[1]
    # 🚨 Check if token is blacklisted
    if r.get(f"blacklist:{token}"):
        logger.warning("🚫 Attempt to use blacklisted token")
        raise HTTPException(status_code=401, detail="Token is blacklisted (logged out)")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"claims": payload}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
