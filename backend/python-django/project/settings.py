"""
Django settings for project
"""
import pymysql
pymysql.install_as_MySQLdb()
import os
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- SECURITY ----------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

DEBUG = True

ALLOWED_HOSTS = ["*"]  # allow docker + frontend

# ---------------- APPLICATIONS ----------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',   # ✅ REQUIRED FOR FRONTEND
    'app',           # your app
]

# ---------------- MIDDLEWARE ----------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ MUST BE FIRST

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # Disable CSRF for API (dev only)
    #'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

# ---------------- TEMPLATES ----------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# ---------------- DATABASE (MySQL) ----------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',

        'NAME': os.getenv("DB_NAME", "auth_app"),
        'USER': os.getenv("DB_USER", "root"),
        'PASSWORD': os.getenv("DB_PASSWORD", "rootpassword"),
        'HOST': os.getenv("DB_HOST", "mysql"),  # docker service name
        'PORT': '3306',

        # ✅ IMPORTANT FIX (avoids weird MySQL errors)
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


# ---------------- PASSWORD VALIDATION ----------------
AUTH_PASSWORD_VALIDATORS = []


# ---------------- INTERNATIONAL ----------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True


# ---------------- STATIC ----------------
STATIC_URL = '/static/'


# ---------------- CORS ----------------
CORS_ALLOW_ALL_ORIGINS = True