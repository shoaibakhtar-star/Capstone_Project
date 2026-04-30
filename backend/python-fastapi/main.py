# ---------------- IMPORTS ----------------
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import BaseModel
import mysql.connector
import os
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta


# ---------------- LOAD ENV ----------------
# Loads variables from root .env file
load_dotenv()


# ---------------- CREATE APP ----------------
# IMPORTANT: Create app ONLY ONCE
app = FastAPI()

# ---------------- CORS MIDDLEWARE ----------------
# Allows frontend (React/Vite) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development (later restrict)
    allow_credentials=False,
    allow_methods=["*"],  # Allow GET, POST, OPTIONS etc.
    allow_headers=["*"],
)


# ---------------- SECURITY ----------------
# Used for protected routes (JWT token)
security = HTTPBearer()


# ---------------- DATABASE CONFIG ----------------
# Reads DB config from .env (shared across all backends)
db_config = {
    "host": os.getenv("DB_HOST"),        # mysql (docker service name)
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}


# ---------------- JWT CONFIG ----------------
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


# ---------------- REQUEST SCHEMA ----------------
# Used for request validation + Swagger docs
class User(BaseModel):
    username: str
    password: str


# ---------------- DATABASE CONNECTION ----------------
def get_db():
    """
    Creates a new DB connection
    """
    return mysql.connector.connect(**db_config)


# ---------------- AUTH UTILS ----------------


def create_token(user_id):
    """
    Create JWT token
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- ROUTES ----------------

@app.get("/health")
def health():
    """
    Health check endpoint (used in DevOps / monitoring)
    """
    try:
        db = get_db()
        db.close()
        return {"status": "healthy Fastapi"}
    except:
        return JSONResponse(content={"status": "unhealthy Fastapi"}, status_code=503)


@app.post("/auth/register")
def register(user: User):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (user.username, user.password),
        )
        db.commit()
        return {"message": "User registered"}
    except mysql.connector.Error:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        cursor.close()
        db.close()

@app.post("/auth/login")
def login(user: User):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id, password FROM users WHERE username = %s",
            (user.username,)
        )
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id, stored_password = result
        if user.password != stored_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_token(user_id)
        return {"access_token": token}
    finally:
        cursor.close()
        db.close()


@app.get("/auth/profile")
def profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Protected route → requires JWT token
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload["user_id"]}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
