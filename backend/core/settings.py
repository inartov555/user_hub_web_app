"""
Settings
"""

import os
import hashlib
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
from django.utils import translation


def env_tuple(name: str, default=()) -> tuple:
    """
    Getting tuple value from list property

    Args:
        name (str): the property value in format (comma separated): one,two,three
        default (tuple): default value

    Returns:
        tuple
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return tuple(default)
    return tuple(prop.strip() for prop in raw.split(",") if prop.strip())

def _attach_request_id(record):
    if not hasattr(record, "request_id"):
        record.request_id = "-"
    return True

def _dir_writable(_path: Path) -> bool:
    _path.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=_path):
        pass
    return True

load_dotenv()

# This variable DEBUG can be (0, 1) which means not debug/debug
DEBUG = os.getenv("DEBUG", "1") == "1"
LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "DEBUG").upper()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = os.getenv("HOST_ARTIFACTS", "workspace/artifacts")
LOG_PATH = Path(LOG_DIR)
LOG_TO_DIR = _dir_writable(LOG_PATH)

# Login session properties start
# Derive a per-boot signing key from your stable secret + BOOT_ID
SECRET_KEY = "user_hub_web_app-secret_key"
BOOT_ID = int(datetime.now(timezone.utc).timestamp())
SIGNING_KEY = hashlib.sha256(f"{SECRET_KEY}.{BOOT_ID}".encode("utf-8")).hexdigest()
JWT_RENEW_AT_SECONDS=int(os.getenv("JWT_RENEW_AT_SECONDS", "100"))
# This becomes your idle timeout window (example: 1800 seconds (30 minutes))
# If the user is inactive for > IDLE_TIMEOUT_SECONDS seconds, their refresh expires and the session ends.
IDLE_TIMEOUT_SECONDS = int(os.getenv("IDLE_TIMEOUT_SECONDS", "60"))
# Short access — forces periodic refreshes
ACCESS_TOKEN_LIFETIME = timedelta(seconds=int(os.getenv("ACCESS_TOKEN_LIFETIME", "120")))
# Turn on rotation so that each refresh "slides" the window forward
ROTATE_REFRESH_TOKENS = bool(os.getenv("ROTATE_REFRESH_TOKENS", "1"))
BLACKLIST_AFTER_ROTATION = bool(os.getenv("BLACKLIST_AFTER_ROTATION", "1"))
ALGORITHM = str(os.getenv("ALGORITHM", "HS256"))
SECRET_KEY = str(os.getenv("SECRET_KEY", "dev-secret"))
SIGNING_KEY = SECRET_KEY
AUTH_HEADER_TYPES = env_tuple("AUTH_HEADER_TYPES", ("Bearer",))
# Login session properties end
ALLOWED_HOSTS = ["*"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s"
        },
        "simple": {"format": "%(levelname)s: %(message)s"},
    },
    "filters": {
        "request_id": {
            "()": "django.utils.log.CallbackFilter",
            "callback": _attach_request_id,
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "simple",
            "filters": ["request_id"],
        },
        **{
            "file_app": {
                "level": LOG_LEVEL,
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": str(LOG_PATH / "app.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": 14,
                "utc": True,
                "encoding": "utf-8",
                "formatter": "verbose" if DEBUG else "simple",
                "filters": ["request_id"],
            },
            "file_errors": {
                "level": LOG_LEVEL,
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": str(LOG_PATH / "errors.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": 14,
                "utc": True,
                "encoding": "utf-8",
                "formatter": "verbose" if DEBUG else "simple",
                "filters": ["request_id"],
            },
        },
        "mail_admins": {
            "level": LOG_LEVEL,
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    "loggers": {
        "profiles": {"handlers": ["console"] + ["file_app"], "level": LOG_LEVEL, "propagate": False},
        "django": {"handlers": ["console"] + ["file_app"], "level": LOG_LEVEL, "propagate": False},
        "django.request": {"handlers": ["console", "mail_admins"] + ["file_app"], "level": LOG_LEVEL,
                           "propagate": False},
        "django.server": {"handlers": ["console"] + ["file_app"], "level": LOG_LEVEL, "propagate": False},
        "django.db.backends": {"handlers": ["console"] + ["file_app"],
                               "level": os.getenv("DJANGO_SQL_LEVEL", LOG_LEVEL), "propagate": False},
        "rest_framework": {"handlers": ["console"] + ["file_app"], "level": LOG_LEVEL, "propagate": False},
        "": {"handlers": ["console"] + ["file_app"], "level": LOG_LEVEL},
    },
}

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
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "profiles.apps.ProfilesConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "profiles.middleware.normalize_language_middleware.NormalizeLanguageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "profiles.middleware.boot_id_enforcer.BootIdEnforcerMiddleware",
    "profiles.middleware.jwt_authentication_middleware.JWTAuthenticationMiddleware",
    "profiles.middleware.boot_id_enforcer.boot_header",
    "profiles.middleware.idle_timeout_middleware.IdleTimeoutMiddleware",
    "profiles.middleware.last_activity_middle_ware.LastActivityMiddleware",
]

USE_I18N = True
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en-us", translation.gettext_lazy("English (US)")),
    ("uk-ua", translation.gettext_lazy("Ukrainian")),
    ("et-ee", translation.gettext_lazy("Estonian")),
    ("fi-fi", translation.gettext_lazy("Finnish")),
    ("cs-cz", translation.gettext_lazy("Czech")),
    ("pl-pl", translation.gettext_lazy("Polish")),
    ("es-es", translation.gettext_lazy("Spanish")),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

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
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
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
    "EXCEPTION_HANDLER": "core.exceptions.localized_exception_handler",
}

SIMPLE_JWT = {
    "SIGNING_KEY": SIGNING_KEY,
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=IDLE_TIMEOUT_SECONDS),
    "ACCESS_TOKEN_LIFETIME": ACCESS_TOKEN_LIFETIME,
    "ROTATE_REFRESH_TOKENS": ROTATE_REFRESH_TOKENS,
    "BLACKLIST_AFTER_ROTATION": BLACKLIST_AFTER_ROTATION,
    "ALGORITHM": ALGORITHM,
    "AUTH_HEADER_TYPES": AUTH_HEADER_TYPES,
    "RENEW_AT_SECONDS": JWT_RENEW_AT_SECONDS,
    "UPDATE_LAST_LOGIN": True,
    "BOOT_ID": BOOT_ID,
    "TOKEN_OBTAIN_SERIALIZER":
        "profiles.serializers.email_or_user_token_create_serializer.EmailOrUsernameTokenCreateSerializer",
    "TOKEN_REFRESH_SERIALIZER": "profiles.serializers.jwt_refresh_serializer.CustomTokenRefreshSerializer",
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
