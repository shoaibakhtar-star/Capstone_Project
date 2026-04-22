from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import mysql.connector
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
app = FastAPI()
security = HTTPBearer()

# ---------------- Config ----------------
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- Schema (for docs + validation) ----------------
class User(BaseModel):
    username: str
    password: str


# ---------------- DB ----------------
def get_db():
    return mysql.connector.connect(**db_config)


# ---------------- Auth Utils ----------------
def hash_password(password):
    return pwd_context.hash(password[:72])


def verify_password(password, hashed):
    return pwd_context.verify(password[:72], hashed)


def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- Routes ----------------

@app.get("/health")
def health():
    try:
        db = get_db()
        db.close()
        return {"status": "healthy"}
    except:
        return {"status": "unhealthy"}


@app.post("/auth/register")
def register(user: User):
    db = get_db()
    cursor = db.cursor()

    username = user.username
    password = user.password

    hashed_password = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password),
        )
        db.commit()
        return {"message": "User registered"}
    except mysql.connector.Error:
        raise HTTPException(status_code=400, detail="User already exists")


@app.post("/auth/login")
def login(user: User):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE username = %s",
        (user.username,)
    )
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, hashed_password = result

    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user_id)

    return {"access_token": token}


@app.get("/auth/profile")
def profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload["user_id"]}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")