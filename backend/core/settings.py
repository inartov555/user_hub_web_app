"""
Settings
"""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
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
MEDIA_ROOT = BASE_DIR / "media"

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
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
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
