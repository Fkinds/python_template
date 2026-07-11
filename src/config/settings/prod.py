from config.settings.base import *  # noqa: F403
from config.settings.base import REST_FRAMEWORK
from config.settings.base import env

DEBUG = False

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS")

# lint-fixme: NoPositionalArgs: django-environ API
SECRET_KEY: str = env("SECRET_KEY")

# ---- Security hardening ----
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# JSON のみを許可し、本番では DRF browsable API を無効化する。
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]
