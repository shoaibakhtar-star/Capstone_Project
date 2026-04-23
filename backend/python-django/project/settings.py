"""
Django settings for project project.
Cloud 3-Tier Backend — raw MySQL queries only, no Django ORM auth system.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-%s2z!!3u%7s#(p@lrc^)yyokp1c!el)k+$(c)qqaek+2%u7m&a')

# JWT config (mirrors FastAPI)
JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-dev-key-change-in-production')
JWT_ALGORITHM  = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DEBUG = True
ALLOWED_HOSTS = ['*']

# ---------------------------------------------------------------------------
# Minimal apps — no Django contrib auth/admin/sessions/contenttypes
# We use raw MySQL queries with our own users table.
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    'app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': []},
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# ---------------------------------------------------------------------------
# MySQL — same creds as FastAPI, our schema is in database/data.sql
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# MySQL — fixed env variable names
# ---------------------------------------------------------------------------
DB_HOST     = os.getenv('DB_HOST', 'mysql')
DB_PORT     = int(os.getenv('MYSQL_PORT', 3306))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME     = os.getenv('DB_NAME', '')

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# ---------------------------------------------------------------------------
# CORS — allow all origins (same as FastAPI allow_origins=["*"])
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES':     [],
    'UNAUTHENTICATED_USER': None,
}

# ---------------------------------------------------------------------------
# Internationalisation / Static files
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True
STATIC_URL    = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

 