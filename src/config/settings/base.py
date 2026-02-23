from pathlib import Path
from typing import Any

import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "config",
    "authors",
    "books",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": ("django.template.backends.django.DjangoTemplates"),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="devdb"),
        "USER": env("POSTGRES_USER", default="devuser"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="devpass"),
        "HOST": env("POSTGRES_HOST", default="db"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}

_V = "django.contrib.auth.password_validation"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"{_V}.UserAttributeSimilarityValidator"},
    {"NAME": f"{_V}.MinimumLengthValidator"},
    {"NAME": f"{_V}.CommonPasswordValidator"},
    {"NAME": f"{_V}.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ja"

TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- S3 Object Storage (RustFS) ----
S3_ENDPOINT_URL: str = env(
    "S3_ENDPOINT_URL",
    default="http://rustfs:9000",
)
S3_ACCESS_KEY: str = env(
    "S3_ACCESS_KEY",
    default="rustfsadmin",
)
S3_SECRET_KEY: str = env(
    "S3_SECRET_KEY",
    default="rustfsadmin",
)
S3_BUCKET_NAME: str = env(
    "S3_BUCKET_NAME",
    default="media",
)

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "endpoint_url": S3_ENDPOINT_URL,
            "access_key": S3_ACCESS_KEY,
            "secret_key": S3_SECRET_KEY,
            "bucket_name": S3_BUCKET_NAME,
            "querystring_auth": False,
            "file_overwrite": False,
            "default_acl": None,
        },
    },
    "staticfiles": {
        "BACKEND": ("django.contrib.staticfiles.storage.StaticFilesStorage"),
    },
}

MEDIA_URL = f"{S3_ENDPOINT_URL}/{S3_BUCKET_NAME}/"

# ---- Discord Notifications ----
DISCORD_WEBHOOK_URL: str = env(
    "DISCORD_WEBHOOK_URL",
    default="",
)

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 10,
}

# ---- Logging ----
LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": ("{levelname} {asctime} {name} {message}"),
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "notifications": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "authors": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "books": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
