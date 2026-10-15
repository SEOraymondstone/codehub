"""
Django settings for the CodeHub project.

Environment-driven configuration: works out of the box with SQLite for local
development and switches to PostgreSQL (or any other engine) through a single
DATABASE_URL variable in production.
"""

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# The test suite runs with DEBUG=False; skip the hashed-manifest storage there
# because collectstatic has not been executed.
TESTING = "test" in sys.argv


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# --------------------------------------------------------------------------
# Core
# --------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-me-)w_1+znpco0*lc#14wf=kj=hr!gv*&(!is8qg@^2yuje9+y9_-",
)

DEBUG = env_bool("DJANGO_DEBUG", True)

if not DEBUG and not TESTING and SECRET_KEY.startswith("django-insecure"):
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY не задан: в режиме DJANGO_DEBUG=false нельзя "
        "использовать встроенный dev-ключ. Укажите случайное значение."
    )

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,[::1]")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")


# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    # CodeHub apps
    "accounts",
    "courses",
    "homework",
    "dashboard",
    "pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "codehub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "pages.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "codehub.wsgi.application"
ASGI_APPLICATION = "codehub.asgi.application"


# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
def build_database() -> dict:
    """Use DATABASE_URL when provided, otherwise fall back to SQLite."""
    url = os.environ.get("DATABASE_URL")
    if url:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        engines = {
            "postgres": "django.db.backends.postgresql",
            "postgresql": "django.db.backends.postgresql",
            "mysql": "django.db.backends.mysql",
        }
        engine = engines.get(parsed.scheme, "django.db.backends.postgresql")
        return {
            "ENGINE": engine,
            "NAME": parsed.path.lstrip("/"),
            "USER": parsed.username or "",
            "PASSWORD": parsed.password or "",
            "HOST": parsed.hostname or "",
            "PORT": str(parsed.port or ""),
            "CONN_MAX_AGE": 600,
        }

    if os.environ.get("POSTGRES_DB"):
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ.get("POSTGRES_USER", "codehub"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 600,
        }

    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }


DATABASES = {"default": build_database()}


# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "pages:landing"


# --------------------------------------------------------------------------
# Internationalisation
# --------------------------------------------------------------------------
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Europe/Moscow")
USE_I18N = True
USE_TZ = True


# --------------------------------------------------------------------------
# Static and media files
# --------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

USE_MANIFEST_STATIC = env_bool("DJANGO_USE_MANIFEST_STATIC", not DEBUG) and not TESTING

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if USE_MANIFEST_STATIC
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------------------------------
# Email (console backend locally, SMTP in production via env)
# --------------------------------------------------------------------------
_EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

# Django 6.1 configures email through MAILERS. SMTP-specific options are only
# passed to an SMTP backend, because unknown options are rejected.
_EMAIL_OPTIONS: dict = {}
if "smtp" in _EMAIL_BACKEND:
    _EMAIL_OPTIONS = {
        "host": os.environ.get("EMAIL_HOST", "localhost"),
        "port": int(os.environ.get("EMAIL_PORT", "587")),
        "username": os.environ.get("EMAIL_HOST_USER", ""),
        "password": os.environ.get("EMAIL_HOST_PASSWORD", ""),
        "use_tls": env_bool("EMAIL_USE_TLS", True),
    }

MAILERS = {
    "default": {
        "BACKEND": _EMAIL_BACKEND,
        "OPTIONS": _EMAIL_OPTIONS,
    },
}

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "CodeHub <noreply@codehub.local>")


# --------------------------------------------------------------------------
# Business configuration (editable through the environment / admin)
# --------------------------------------------------------------------------
CODEHUB_SITE = {
    "name": os.environ.get("CODEHUB_NAME", "CodeHub"),
    "tagline": os.environ.get(
        "CODEHUB_TAGLINE", "Онлайн-курс по программированию: от нуля до первого оффера"
    ),
    "price_from": os.environ.get("CODEHUB_PRICE", "$100"),
    "phone": os.environ.get("CODEHUB_PHONE", "+7 (900) 000-00-00"),
    "phone_secondary": os.environ.get("CODEHUB_PHONE_2", "+7 (900) 111-11-11"),
    "email": os.environ.get("CODEHUB_EMAIL", "hello@codehub.dev"),
    "telegram": os.environ.get("CODEHUB_TELEGRAM", "https://t.me/codehub"),
    "whatsapp": os.environ.get("CODEHUB_WHATSAPP", "https://wa.me/79000000000"),
    "instagram": os.environ.get("CODEHUB_INSTAGRAM", "https://instagram.com/codehub"),
    "youtube": os.environ.get("CODEHUB_YOUTUBE", "https://youtube.com/@codehub"),
    "github": os.environ.get("CODEHUB_GITHUB", "https://github.com/codehub"),
}

# Maximum size (bytes) accepted for a single homework upload -> 1 GB.
HOMEWORK_MAX_UPLOAD_SIZE = int(
    os.environ.get("HOMEWORK_MAX_UPLOAD_SIZE", str(1024 * 1024 * 1024))
)

# Файлы больше этого размера стримятся во временный файл, а не держатся в памяти.
FILE_UPLOAD_MAX_MEMORY_SIZE = int(
    os.environ.get("FILE_UPLOAD_MAX_MEMORY_SIZE", str(5 * 1024 * 1024))
)

# Ограничивает только необработанные поля формы (без файлов).
DATA_UPLOAD_MAX_MEMORY_SIZE = int(
    os.environ.get("DATA_UPLOAD_MAX_MEMORY_SIZE", str(10 * 1024 * 1024))
)

# Where teachers are notified about new submissions (defaults to console mail).
TEACHER_NOTIFICATION_EMAIL = os.environ.get("TEACHER_NOTIFICATION_EMAIL", "")


# --------------------------------------------------------------------------
# Security hardening (only applied in production where HTTPS terminates)
# --------------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # Never force HTTPS inside the test client, which speaks plain HTTP.
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True) and not TESTING
    SESSION_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", True)
    CSRF_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", True)
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "root": {"handlers": ["console"], "level": "INFO"},
    }
