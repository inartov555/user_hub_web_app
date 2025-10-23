"""
Settings
"""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv("DEBUG", "1") == "1"
# SESSION_COOKIE_AGE = os.getenv("SESSION_COOKIE_AGE", str(30 * 60))  # defaults to 30 minutes
# IDLE_TIMEOUT_SECONDS = os.getenv("IDLE_TIMEOUT_SECONDS", str(30 * 60))  # defaults to 30 minutes
# Refresh expiry on every request (rolling inactivity timeout)
# SESSION_SAVE_EVERY_REQUEST = os.getenv("SESSION_SAVE_EVERY_REQUEST", "1")
# The property SESSION_EXPIRE_AT_BROWSER_CLOSE affects also page reload
# SESSION_EXPIRE_AT_BROWSER_CLOSE = os.getenv("SESSION_EXPIRE_AT_BROWSER_CLOSE", "1")  # or True if you prefer
# SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "1")  # if using HTTPS

# Login session properties start
ACCESS_COOKIE_NAME = str(os.getenv("ACCESS_COOKIE_NAME", "access"))
REFRESH_COOKIE_NAME = str(os.getenv("REFRESH_COOKIE_NAME", "refresh"))
RENEW_AT_SECONDS = int(os.getenv("RENEW_AT_SECONDS", "60"))
COOKIE_PATH = str(os.getenv("COOKIE_PATH", "/"))
COOKIE_DOMAIN = str(os.getenv("COOKIE_DOMAIN", ""))
COOKIE_SAMESITE = str(os.getenv("COOKIE_SAMESITE", "Lax"))
COOKIE_SECURE = bool(os.getenv("COOKIE_SECURE", "0"))
COOKIE_HTTPONLY = bool(os.getenv("COOKIE_HTTPONLY", "1"))

# This becomes your idle timeout window (example: 1800 seconds (30 minutes))
# If the user is inactive for > IDLE_TIMEOUT_SECONDS seconds, their refresh expires and the session ends.
IDLE_TIMEOUT_SECONDS = int(os.getenv("IDLE_TIMEOUT_SECONDS", "100"))
# Short access — forces periodic refreshes
ACCESS_TOKEN_LIFETIME = int(os.getenv("ACCESS_TOKEN_LIFETIME", "60"))
# Turn on rotation so that each refresh "slides" the window forward
ROTATE_REFRESH_TOKENS = bool(os.getenv("ROTATE_REFRESH_TOKENS", "1"))
BLACKLIST_AFTER_ROTATION = bool(os.getenv("BLACKLIST_AFTER_ROTATION", "1"))
ALGORITHM = str(os.getenv("ALGORITHM", "HS256"))
SECRET_KEY = str(os.getenv("SECRET_KEY", "dev-secret"))
SIGNING_KEY = SECRET_KEY
AUTH_HEADER_TYPES = list(os.getenv("AUTH_HEADER_TYPES", ["Bearer",]))
# Login session properties end
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "djoser",
    "drf_spectacular",
    "profiles.apps.ProfilesConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "profiles.middleware.jwt_authentication_middleware.JWTAuthenticationMiddleware",
    "profiles.middleware.idle_timeout_middleware.IdleTimeoutMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "profiles.middleware.last_activity_middle_ware.LastActivityMiddleware",
]

ROOT_URLCONF = "core.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "usersdb"),
        "USER": os.getenv("POSTGRES_USER", "users"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "users"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}
# Uncomment for SQLite local quickstart
# DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CORS_ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "IDLE_TIMEOUT_SECONDS": IDLE_TIMEOUT_SECONDS,
    "ACCESS_TOKEN_LIFETIME": ACCESS_TOKEN_LIFETIME,
    "ROTATE_REFRESH_TOKENS": ROTATE_REFRESH_TOKENS,
    "BLACKLIST_AFTER_ROTATION": BLACKLIST_AFTER_ROTATION,
    "ALGORITHM": ALGORITHM,
    "SECRET_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": AUTH_HEADER_TYPES,
}

JWT_COOKIE = {
    "ACCESS_COOKIE_NAME": ACCESS_COOKIE_NAME,
    "REFRESH_COOKIE_NAME": REFRESH_COOKIE_NAME,
    "RENEW_AT_SECONDS": RENEW_AT_SECONDS,
    "COOKIE_PATH": COOKIE_PATH,
    "COOKIE_DOMAIN": COOKIE_DOMAIN,
    "COOKIE_SAMESITE": COOKIE_SAMESITE,
    "COOKIE_SECURE": COOKIE_SECURE,
    "COOKIE_HTTPONLY": COOKIE_HTTPONLY,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Users API",
    "DESCRIPTION": "Auth, profiles, users table, excel import",
    "VERSION": "1.0.0",
}

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "password-reset/confirm/{uid}/{token}/",
    "USERNAME_RESET_CONFIRM_URL": "username-reset/confirm/{uid}/{token}/",
    "ACTIVATION_URL": "activate/{uid}/{token}/",
    "LOGIN_FIELD": "email",
    "SEND_ACTIVATION_EMAIL": False,   # dev: no activation step
    "SERIALIZERS": {
        "token_create": \
            "profiles.serializers.email_or_user_token_create_serializer.EmailOrUsernameTokenCreateSerializer",
        "user_create": "profiles.serializers.user_create_serializer.UserCreateSerializer",
        "user": "profiles.serializers.user_serializer.UserSerializer",
        "current_user": "profiles.serializers.user_serializer.UserSerializer"
    },
    "PERMISSIONS": {
        "token_create": ["rest_framework.permissions.AllowAny"],
        "token_destroy": ["rest_framework.permissions.IsAuthenticated"],
        "jwt_create": ["rest_framework.permissions.AllowAny"],
        "jwt_refresh": ["rest_framework.permissions.AllowAny"],
        "user_list": ["rest_framework.permissions.IsAuthenticated"],
        "user": ["rest_framework.permissions.IsAuthenticated"],
        "current_user": ["rest_framework.permissions.IsAuthenticated"],
    },
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
