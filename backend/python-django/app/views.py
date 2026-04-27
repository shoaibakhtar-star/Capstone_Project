import json
import os
import mysql.connector   # ✅ ADD THIS

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_db():
    return mysql.connector.connect(**db_config)


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


# ---------------- ROUTES ----------------

def health(request):
    return JsonResponse({"status": "healthy django"})


@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    data = json.loads(request.body)

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (data["username"], hash_password(data["password"]))
        )
        db.commit()
        return JsonResponse({"message": "User registered"})
    except:
        return JsonResponse({"detail": "User already exists"}, status=400)


@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    data = json.loads(request.body)

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE username = %s",
        (data["username"],)
    )
    result = cursor.fetchone()

    if not result:
        return JsonResponse({"detail": "Invalid credentials"}, status=401)

    user_id, hashed_password = result

    if not verify_password(data["password"], hashed_password):
        return JsonResponse({"detail": "Invalid credentials"}, status=401)

    token = create_token(user_id)

    return JsonResponse({"access_token": token})


def profile(request):
    auth = request.headers.get("Authorization")

    if not auth:
        return JsonResponse({"detail": "No token"}, status=401)

    token = auth.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return JsonResponse({"user_id": payload["user_id"]})
    except:
        return JsonResponse({"detail": "Invalid token"}, status=401)